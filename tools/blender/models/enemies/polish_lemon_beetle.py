"""FRUIT's lemon beetle (sheet ', written x27 in models.cfg: sprites 16 18 above 54 56 above 92 94, 2x2 each; enemies 1238
to 1243 of episode 5, the top layer), polished (2026-10-22, round 32; it replaces wave3_ae_lemon.py's lemon beetle, a
ribbed ellipsoid and a relief painted pixel by pixel). The levels always put its six sprites together as one 48 x 84
picture, the sheet's own layout (FRUIT's events 7 at t 1650, 1750, 2200, 3400, 4000, 4200, 4250 and 4300: 1238 (' 16)
at (x, y - 56), 1239 (' 18) at (x + 24, y - 56), 1240 (' 54) at (x, y - 28), 1241 (' 56) at (x + 24, y - 28), 1242
(' 92) at (x, y), 1243 (' 94) at (x + 24, y), all six with one link, moving with background 3). Each piece is an
enemy of its own (armour 60, one frame, no damaged look, no guns), but they share their link, and tyrian2.c destroys
every enemy of a link when one of them is shot down: the beetle always dies whole, no piece is ever seen alone (it
only leaves the screen's bottom a row at a time). No other enemy, launched ones included, shows these sprites, no
episode 6 level takes these waves, and none of the six is another sprite's pixels mirrored, turned or in other ramps;
the picture is its own mirror image about its middle (x 0: column c and 47 - c alike but for the shading of a few
pixels and one notch at row 42), so the beetle is built symmetric.

As the sprites and their 4x upscales draw it (columns and rows of the 48 x 84 picture; every pixel in ramp 7's yellows,
0x7a orange to 0x7f white): a big lemon-yellow earwig of a beetle crawling down the screen.
- Its abdomen (rows 18-45, columns 4-43): a broad domed carapace in five overlapping plates, each lit along its lower
  edge (0x7d at rows 21, 26, 31, 36 and 42) over the dark crease (0x7b) where it drops onto the next, the creases bowed
  up the screen in the middle and running down at the sides into a groove (0x7a-0x7b, columns 8-11 and 36-39) that
  parts the plated back from the rolled margin round it, lit at its upper left (0x7d, column 7).
- At its top corners two forceps (cerci, rows 0-18, seven pixels wide), rising straight up the screen from the
  shoulders and curving in to points that nearly meet over the middle at the picture's top edge, lit outside (0x7c),
  darker along their inner edges (0x7a-0x7b).
- Under a deep crease across the waist (0x7a, row 45) the head (rows 45-62), as wide as the picture: two big lemon
  slices for eyes (round, 15 pixels across, their middles at columns 14 and 33 of row 54: pale juice 0x7d-0x7e in eight
  segments between white membranes 0x7f, a white core), a narrow bridge between them, the cheeks at its sides (columns
  0-6) the roots of the mandibles.
- Two long mandibles (rows 60-83): from the cheeks they hang down the screen, broad at their roots, and curve in to
  points (columns 14-15 and 32-33 of row 83), lit outside (0x7c, 0x7d along the left one), darker inside.

Built as such a creature, modelled in the picture's plane (x, y as the sprite draws them, z up) and then sheared along
the game camera's line of sight (y - z tan 20, the normals with it: polish_lava_grub.shear_to_camera), so that the
camera sees every point where the sprite draws it, however high it stands:
- The body (abdomen and head in one closed solid over the class map's s, h and e pixels, mirrored and blurred:
  BodyField; polish_torm_beetle.Solid's heights, rims and normals over a mesh of its own, LinedSolid: a constrained
  Delaunay triangulation of the region's contour, of lines along every crease (its bottom, the middle of its drop, the
  lip's top and the lip's light band), the groove, the waist and round the sockets, and of a coarse grid between
  them, so that the creases are clean edges and the plates cost few triangles; the belly's flat middle in a few large
  faces): the abdomen a superellipsoid dome (SHELL) carrying the plates (each rising towards its lower edge in a
  rounded tile and dropping into the crease under it, the creases bowed: CREASES, BOW, PLATE_AMP), the groove along
  the plated back's sides (GROOVE) with the margin rolled outside it, the plates fading out on the margin; the waist
  (NECK_DROP) where the last plate's lip drops onto the head; the head a lower broad dome (HEAD) with the cheeks
  swelling at its sides, a low brow round each of the two sockets the slices sit in; a faint dimpling of lemon peel
  over everything (PEEL: a sum of plane waves, the same every run); the rim at z 0, the flat belly under it (BELLY),
  rounded up to the rim.
- The slices: a polar mesh each, lying flat (the camera sees them round): a glossy rind rolled over the rim of the
  socket, the white pith inside it, eight segments of juice cushioned between eight white membranes (cut along smooth
  contours: split_contour), lighter along their crests, a white core.
- The forceps and the mandibles: tubes along the sprites' curves (polish_torm_beetle.tube: lens-shaped sections lying
  flat, closed to points), their roots sunk into the body, the right ones the left ones mirrored.
- Painted in ramp 7's yellows: on the plates by where a face lies (body_zone: a crease's drop 0x7a deep down and 0x7b
  higher up, the lip's top 0x7d, the waist 0x7a and 0x7b), elsewhere in bands of the light it gets (light_value: facing
  the game's sun and up, from the surface without the dimples; 0x7b, 0x7c, 0x7d, cut along smooth contours), the
  forceps' and mandibles' inner sides darker (as the sprite's: 0x7a-0x7e by light); every yellow glowing a little in
  its own colour (0.07-0.15: the slanted camera would otherwise show them olive), glossy (lemon peel); the slices'
  juice and membranes glowing more (0.16-0.44), so that the eyes read as the sprite's bright slices.
Cut into the six pieces in the picture's plane along the sprites' edges (x 0; y 14 and -14), before the shear, so each
piece holds what its sprite draws and its cut faces lie along the camera's line of sight (polish_coral_manta.cut: the
caps the body's inside, 0x7c); each piece moved so that its sprite's middle is its origin, its parts joined, every mesh
triangulated (polish_k_pod.triangulate: the same output with and without --check). Deterministic: no random numbers,
no booleans.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up. The whole's origin is the picture's
middle (its pixel edge 24, 42): column c is x = c + 0.5 - 24, row r is y = 41.5 - r. The pieces' origins (their
sprites' middles): 16 (-12, 28), 18 (12, 28), 54 (-12, 0), 56 (12, 0), 92 (-12, -28), 94 (12, -28). In the picture's
plane the rim lies at z 0, the belly at about -2.2, the plates' top at 8.9, the head at 5, the slices at 5.5; drawn at
their origins on the top layer (models.cfg origin).

models.cfg (unchanged): model lemon_beetle_tl .. _br enemies/lemon_beetle_*.glb origin, sprite x27 16 lemon_beetle_tl
yaw=0 (18 _tr, 54 _ml, 56 _mr, 92 _bl, 94 _br).

Replaces wave3_ae_lemon.py's lemon beetle (its section "' 16 18 / 54 56 / 92 94: the lemon beetle": LEMON, BODY_C,
BODY_R, HEAD_C, HEAD_R, SLICE_X, SLICE_Y, SLICE_R, ribbed(), lemon_beetle_whole(), the kit.PROTECT += [...] line and the
kit.pieced("lemon_beetle", ...) registration, its docstring paragraph) and wave3_ae_art.py's LEMON (read only by it).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the whole's silhouette as the
camera sees it and from straight above, and each piece's, against enemy_x27.png), --preview <prefix> (the whole's top and
3/4 views; --pieces 1 also each piece's), --only <name,...> (pieces to export), --whole <file.glb> (the sheared whole as
well, for looking at), --stats 1.
"""
import math
import os
import sys

import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Vector, geometry

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
import polish_machine_kit as mk  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402
from polish_deli_boss import join, drop_unused  # noqa: E402
from polish_coral_manta import cut, split_contour  # noqa: E402
from polish_orb_red import band_split  # noqa: E402
from polish_torm_beetle import Solid, smax, sstep, tube  # noqa: E402

VIEW_TILT = 20.0                  # the game's camera: this far off straight down, from the bottom of the screen
TAN_T = math.tan(math.radians(VIEW_TILT))
LIGHT = Vector((-0.6, 0.6, 1.0)).normalized()   # towards the game's sun (render_gpu.c: from above and the top left)
FLAT = LIGHT.z
W, H = 48, 84
GRID = 1.15                       # the body's coarse grid between its lines (pixels)
LINE_STEP = 0.55                  # the points along the outline (the lines' own points are 0.7 apart)

# --- The sprites' pixels ---------------------------------------------------------------------------------------------
# The left half of the picture (columns 0-23; the right half is its mirror image), one character a pixel: c the
# forceps, s the abdomen, h the head and cheeks, e the slices' juice and membranes, m the mandibles; '.' none.
LEFT = [
    "..................ccccc.", "................ccccccc.", "...............ccccccc..", "..............ccccccc...",
    ".............ccccccc....", "............ccccccc.....", "............ccccccc.....", "...........ccccccc......",
    "...........ccccccc......", "...........ccccccc......", "..........ccccccc.......", "..........ccccccc.......",
    "..........ccccccc.......", "..........ccccccc.......", "..........ccccccc.......", "..........ccccccc.......",
    "..........ccccccc.......", "..........ccccccc.......", "...........cccccc...ssss", "..........ssssssssssssss",
    ".........sssssssssssssss", "........ssssssssssssssss", ".......sssssssssssssssss", "......ssssssssssssssssss",
    "......ssssssssssssssssss", ".....sssssssssssssssssss", ".....sssssssssssssssssss", ".....sssssssssssssssssss",
    "....ssssssssssssssssssss", "....ssssssssssssssssssss", "....ssssssssssssssssssss", "....ssssssssssssssssssss",
    "....ssssssssssssssssssss", "....ssssssssssssssssssss", "....ssssssssssssssssssss", "....ssssssssssssssssssss",
    ".....sssssssssssssssssss", ".....sssssssssssssssssss", ".....sssssssssssssssssss", "......ssssssssssssssssss",
    "......ssssssssssssssssss", ".......sssssssssssssssss", "........ssssssssssssssss", "........ssssssssssssssss",
    "......ssssssssssssssssss", ".....sssssssssssssssssss", "....hhhhhhhhhhhhhhhhhhhh", "...hhhhhhhhheeeeehhhhhhh",
    "..hhhhhhhheheeeeeeehhhhh", "..hhhhhhheeeheeheeeehhhh", ".hhhhhhheeeeeeeeheeeehhh", ".hhhhhhheeeeeeeeeeeehhhh",
    ".hhhhhheeheeeeeeeeeeeehh", "hhhhhhheeeheeeeeeeeeeehh", "hhhhhhheeeeeeeeeeeeeeehh", "hhhhhhheeeeeeeeeeeeeeehh",
    "hhhhhhheeeeeeeeeeeeehehh", "hhhhhhhheeeeeeeeeeehehhh", "hhhhhhhheeeeeeeeeeeeehhh", "hhhhhhhhheeeeeeeeheehhhh",
    "mmmmmmmmmmeeheeeehehh...", ".mmmmmmmmmhheeeeehhh....", ".mmmmmmmmmhhhhhhhh......", ".mmmmmmmmmmmm...........",
    "..mmmmmmmmmmm...........", "..mmmmmmmmmmm...........", "...mmmmmmmmm............", "....mmmmmmmm............",
    ".....mmmmmmm............", ".....mmmmmmm............", ".....mmmmmmm............", ".....mmmmmmm............",
    ".....mmmmmmm............", ".....mmmmmmm............", "......mmmmmm............", "......mmmmmm............",
    "......mmmmmmm...........", ".......mmmmmm...........", ".......mmmmmm...........", "........mmmmmm..........",
    ".........mmmmm..........", "...........mmmm.........", ".............mmm........", "..............mm........",
]
# (Two pixels the sheet leaves out of the outline, at row 46 column 18 and row 60 column 7, are filled in.)


def picture():
    """The whole picture's class map (84 rows of 48 characters)."""
    return [row + row[::-1] for row in LEFT]


class BodyField:
    """The pixels of some classes, blurred (a Gaussian of sigma pixels): 0 outside, 1 inside, at any (x, y); minus
    `level` (so the region is where it is > 0)."""

    def __init__(self, classes, sigma=0.7, level=0.5):
        pad = 6
        rows = picture()
        m = np.zeros((H + 2 * pad, W + 2 * pad))
        for r, row in enumerate(rows):
            for c, ch in enumerate(row):
                if ch in classes:
                    m[r + pad, c + pad] = 1.0
        rad = int(math.ceil(3 * sigma))
        t = np.arange(-rad, rad + 1)
        ker = np.exp(-t * t / (2 * sigma * sigma))
        ker /= ker.sum()
        m = np.apply_along_axis(lambda v: np.convolve(v, ker, mode="same"), 0, m)
        m = np.apply_along_axis(lambda v: np.convolve(v, ker, mode="same"), 1, m)
        self.m, self.pad, self.level = m, pad, level

    def __call__(self, x, y):
        x = np.atleast_1d(np.asarray(x, float))
        y = np.atleast_1d(np.asarray(y, float))
        fc = x + 23.5 + self.pad
        fr = 41.5 - y + self.pad
        h, w = self.m.shape
        c0 = np.clip(np.floor(fc).astype(int), 0, w - 2)
        r0 = np.clip(np.floor(fr).astype(int), 0, h - 2)
        tc = np.clip(fc - c0, 0.0, 1.0)
        tr = np.clip(fr - r0, 0.0, 1.0)
        m = self.m
        return (m[r0, c0] * (1 - tc) * (1 - tr) + m[r0, c0 + 1] * tc * (1 - tr) + m[r0 + 1, c0] * (1 - tc) * tr +
                m[r0 + 1, c0 + 1] * tc * tr) - self.level


class LinedSolid(Solid):
    """polish_torm_beetle.Solid over a constrained Delaunay triangulation instead of a regular grid: the region's
    contour (traced on a fine grid, resampled every LINE_STEP), lines inside it where the surface bends fast (the
    creases, the groove, the waist, the sockets: polylines, also resampled) as constraints, and a coarse hexagonal grid
    between them (spacing), so that the creases are clean edges and the plates between them cost few triangles."""

    def __init__(self, f, bbox, spacing, lines):
        tracer = Solid(f, bbox, spacing=0.35)
        rim_edges = [e for e in tracer.bm.edges if len(e.link_faces) == 1]
        loops = chain(rim_edges)
        tracer.bm.free()
        boundary, edges = [], []
        for loop in loops:
            ring = resample_loop(loop, LINE_STEP)
            start = len(boundary)
            boundary += ring
            edges += [(start + i, start + (i + 1) % len(ring)) for i in range(len(ring))]
        self.seg_a = np.array([boundary[a] for a, _ in edges])
        self.seg_b = np.array([boundary[b] for _, b in edges])
        points = list(boundary)
        # the lines: inside the region, away from the outline
        for line in lines:
            pts = resample_line(line, LINE_STEP)
            arr = np.array(pts)
            keep = (f(arr[:, 0], arr[:, 1]) > 0.04) & (self.dist(arr[:, 0], arr[:, 1]) > 0.35)
            run = []
            for p_, kp in zip(pts, keep):
                if kp:
                    run.append(p_)
                    continue
                if len(run) > 1:
                    start = len(points)
                    points += run
                    edges += [(start + i, start + i + 1) for i in range(len(run) - 1)]
                run = []
            if len(run) > 1:
                start = len(points)
                points += run
                edges += [(start + i, start + i + 1) for i in range(len(run) - 1)]
        constrained = np.array(points)
        x0, x1, y0, y1 = bbox
        dy = spacing * math.sqrt(3) / 2
        grid = []
        for j in range(int(math.ceil((y1 - y0) / dy)) + 1):
            for i in range(int(math.ceil((x1 - x0) / spacing)) + 2):
                grid.append((x0 + i * spacing + (spacing / 2 if j % 2 else 0.0), y0 + j * dy))
        grid = np.array(grid)
        keep = f(grid[:, 0], grid[:, 1]) > 0.0
        grid = grid[keep]
        keep = self.dist(grid[:, 0], grid[:, 1]) > 0.5 * spacing
        keep &= slice_distance(grid[:, 0], grid[:, 1]) > SOCKET_EMPTY
        grid = grid[keep]
        near = np.full(len(grid), np.inf)
        for s0 in range(0, len(constrained), 512):
            c = constrained[s0:s0 + 512]
            d2 = ((grid[:, None, :] - c[None, :, :]) ** 2).sum(2).min(1)
            near = np.minimum(near, d2)
        grid = grid[near > (0.45 * spacing) ** 2]
        points += [tuple(p_) for p_ in grid]
        verts, _e, faces, orig, *_ = geometry.delaunay_2d_cdt([Vector(p_) for p_ in points], edges, [], 0, 1e-6)
        tris = [fc for fc in faces if len(fc) == 3]
        cent = np.array([[sum(verts[i].x for i in fc) / 3, sum(verts[i].y for i in fc) / 3] for fc in tris])
        inside = f(cent[:, 0], cent[:, 1]) > 0.0
        bm = bmesh.new()
        bverts = [bm.verts.new((v.x, v.y, 0.0)) for v in verts]
        for fc, ok in zip(tris, inside):
            if ok:
                try:
                    bm.faces.new([bverts[i] for i in fc])
                except ValueError:
                    pass
        bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        for fc in bm.faces:
            fc.normal_update()
            if fc.normal.z < 0:
                fc.normal_flip()
        self.f = f
        self.bm = bm
        on_outline = set()
        boundary_set = {(round(p_[0], 6), round(p_[1], 6)) for p_ in boundary}
        for v in bm.verts:
            if (round(v.co.x, 6), round(v.co.y, 6)) in boundary_set:
                on_outline.add(v)
        values = {}
        for v in bm.verts:
            values[v] = 0.0 if v in on_outline else float(f([v.co.x], [v.co.y])[0])
        self.vals = {"f": values}
        rim = {v for e in bm.edges if len(e.link_faces) == 1 for v in e.verts}
        self.rim = rim | on_outline
        self.tops = set(bm.faces)

    def shape(self, *args, **kwargs):
        """Solid.shape, then the belly's flat middle in a few large faces (its inner points dissolved)."""
        super().shape(*args, **kwargs)
        bm = self.bm
        bm.normal_update()
        flat = []
        for v in bm.verts:
            if v in self.rim or not v.link_faces:
                continue
            if all(fc not in self.tops and fc.normal.z < -0.9995 for fc in v.link_faces):
                flat.append(v)
        flat.sort(key=lambda v: (round(v.co.x, 5), round(v.co.y, 5)))
        if flat:
            bmesh.ops.dissolve_verts(bm, verts=flat, use_face_split=False, use_boundary_tear=False)
        self.bottoms = {fc for fc in bm.faces if fc not in self.tops}


def chain(edges):
    """The boundary edges as closed loops of (x, y) points, in a fixed order."""
    nxt = {}
    for e in edges:
        a, b = e.verts
        nxt.setdefault(a, []).append(b)
        nxt.setdefault(b, []).append(a)
    seen = set()
    loops = []
    for start in sorted(nxt, key=lambda v: (round(v.co.x, 5), round(v.co.y, 5))):
        if start in seen:
            continue
        loop = [start]
        seen.add(start)
        prev, cur = None, start
        while True:
            options = [v for v in nxt[cur] if v is not prev and v not in seen]
            if not options:
                break
            prev, cur = cur, options[0]
            seen.add(cur)
            loop.append(cur)
        if len(loop) > 8:
            loops.append([(v.co.x, v.co.y) for v in loop])
    return loops


def resample_loop(points, step):
    pts = [np.array(p_) for p_ in points] + [np.array(points[0])]
    lengths = [0.0]
    for a, b in zip(pts, pts[1:]):
        lengths.append(lengths[-1] + float(np.linalg.norm(b - a)))
    total = lengths[-1]
    n = max(8, int(round(total / step)))
    out, j = [], 0
    for i in range(n):
        t = total * i / n
        while lengths[j + 1] < t:
            j += 1
        u = (t - lengths[j]) / max(lengths[j + 1] - lengths[j], 1e-9)
        p_ = pts[j] * (1 - u) + pts[j + 1] * u
        out.append((float(p_[0]), float(p_[1])))
    return out


def resample_line(points, step):
    pts = [np.array(p_, float) for p_ in points]
    out = [tuple(pts[0])]
    for a, b in zip(pts, pts[1:]):
        n = max(1, int(math.ceil(float(np.linalg.norm(b - a)) / step)))
        for i in range(1, n + 1):
            p_ = a + (b - a) * (i / n)
            out.append((float(p_[0]), float(p_[1])))
    return out


# --- The body's heights ----------------------------------------------------------------------------------------------
# The abdomen: a superellipsoid dome over the plated back (its middle, radii in plan, power, height).
SHELL_C, SHELL_R, SHELL_P, SHELL_H = (0.0, 9.6), (21.4, 14.6), 2.6, 8.4
# The plates: the creases' middles (y at x 0; the first is the top edge's, above the first plate), bowed down the
# screen by BOW x^2 towards the sides; each plate rises PLATE_AMP from its upper edge to its lip, the last LIP of its
# span, and drops into the crease; they fade out over PLATE_FADE (|x|) on the margin.
CREASES = [24.6, 19.6, 14.6, 9.6, 4.1, -1.4]
BOW = 0.03
PLATE_AMP, LIP, PLATE_ROUND = 1.75, 0.2, 2.2
LIP_LIGHT = (0.18, 0.75)             # the lip's rounded top: this much of the span above its drop, this much lighter
PLATE_FADE = (11.6, 13.8)
# The groove along the plated back's sides: a superellipse (its middle, half-width, half-height, power) from y GROOVE_Y
# down to the waist; its depth and half-width; the margin outside it rolled up by MARGIN.
GROOVE = ((0.0, 7.2), 14.6, 13.2, 3.0)
GROOVE_Y = (-3.0, 18.0)
GROOVE_DEPTH, GROOVE_W = 1.0, 0.85
MARGIN = 0.65
# The waist: under the last crease the abdomen falls NECK_DROP more over NECK_SPAN pixels onto the head.
NECK_DROP, NECK_SPAN = 2.6, 2.4
# The head: a broad dome (half-width, power, height), rising from the waist (y HEAD_RISE) to its full height, low at
# its front; the cheeks swell at its sides (middle (|x|, y), radii, height).
HEAD_A, HEAD_P, HEAD_H = 26.0, 2.2, 5.2
HEAD_RISE = (-3.2, -7.5)
HEAD_FRONT = (-15.0, -22.0, 0.72)    # from this y to that, its height falls to this fraction
CHEEK = ((20.2, -15.4), (3.1, 5.2), 1.5)
BROW = (0.55, 0.55, 0.75)            # a ridge round each socket: how far out of the rim, its height, half-width
# The slices (the eyes): their middles, radius, the height of their face, the sockets round them a little lower.
SLICE_C = (9.5, -13.0)
SLICE_R = 7.45
SLICE_Z = 5.55
SOCKET = 0.45                        # the head within a slice's rim lies this far under its rind's foot
# The body's mesh: lines this far under the last crease (the waist's fall), circles round the slices' middles, no
# grid points within SOCKET_EMPTY of them (the head there lies under the slices).
NECK_LINES = (0.9, 1.8)
SOCKET_LINES = (SLICE_R - 0.4, SLICE_R + 0.05, SLICE_R + 1.15)
SOCKET_EMPTY = SLICE_R - 0.5
# The lemon peel: plane waves (direction in degrees, wavelength, phase), amplitude.
PEEL_WAVES = [(12.0, 1.35, 0.3), (71.0, 1.21, 1.9), (133.0, 1.43, 4.1), (164.0, 1.17, 2.6), (37.0, 0.97, 5.3),
              (101.0, 1.07, 0.9), (149.0, 0.91, 3.7), (55.0, 1.61, 2.2)]
PEEL = 0.015
# The belly: flat, this far under the rim, rounded up to it over BELLY_ROUND pixels.
BELLY, BELLY_ROUND = 2.2, 2.4
EDGE_ROUND = 2.2                     # the top rounds down to the rim over this many pixels


def superellipse_radius(x, y, centre, radii, power):
    u = np.abs(x - centre[0]) / radii[0]
    v = np.abs(y - centre[1]) / radii[1]
    return (u ** power + v ** power) ** (1.0 / power)


def plate_profile(x, y):
    """The plates' offset over the dome (-PLATE_AMP/2 .. PLATE_AMP/2), a crease value (1 in a crease's drop, 0 on a
    plate) and the lips' tops (1 there)."""
    yb = y + BOW * x * x                 # unbowed
    offset = np.zeros_like(y)
    crease = np.zeros_like(y)
    lip = np.zeros_like(y)
    for upper, lower in zip(CREASES, CREASES[1:]):
        span = upper - lower
        w = (yb - lower) / span           # 0 at the crease under the plate, 1 at its upper edge
        inside = (w >= 0.0) & (w < 1.0)
        rise = 1.0 - np.clip((w - LIP) / (1.0 - LIP), 0.0, 1.0) ** PLATE_ROUND
        wl = np.clip(w / LIP, 0.0, 1.0)
        drop = np.sqrt(np.clip(1.0 - (1.0 - wl) ** 2, 0.0, 1.0))
        prof = np.where(w >= LIP, rise, drop)
        offset = np.where(inside, PLATE_AMP * (prof - 0.5), offset)
        crease = np.where(inside & (w < LIP), 1.0 - wl, crease)
        lip = np.where(inside & (w >= LIP) & (w < LIP + LIP_LIGHT[0]), 1.0, lip)
    return offset, crease, lip


def groove_profile(x, y):
    (gx, gy), ga, gb, gp = GROOVE
    dy = np.clip(np.abs(y - gy) / gb, 0.0, 1.0)
    xg = ga * (1.0 - dy ** gp) ** (1.0 / gp)
    g = np.abs(x) - xg
    along = sstep(GROOVE_Y[0] - 1.5, GROOVE_Y[0] + 0.5, y) * sstep(GROOVE_Y[1] + 1.5, GROOVE_Y[1] - 1.0, y)
    return np.exp(-(g / GROOVE_W) ** 2) * along, sstep(-0.3, 1.6, g) * along


def peel(x, y):
    out = np.zeros_like(x)
    for angle, wave, phase in PEEL_WAVES:
        a = math.radians(angle)
        out += np.sin((x * math.cos(a) + y * math.sin(a)) * 2 * math.pi / wave + phase)
    return PEEL * out / math.sqrt(len(PEEL_WAVES) / 2)


def slice_distance(x, y):
    """How far (x, y) lies from the nearer slice's middle."""
    return np.hypot(np.abs(x) - SLICE_C[0], y - SLICE_C[1])


def shell_top(x, y):
    s = superellipse_radius(x, y, SHELL_C, SHELL_R, SHELL_P)
    dome = SHELL_H * np.sqrt(np.clip(1.0 - s * s, 0.0, 1.0))
    offset, _, _ = plate_profile(x, y)
    fade = sstep(PLATE_FADE[1], PLATE_FADE[0], np.abs(x))
    groove, outside = groove_profile(x, y)
    z = dome + offset * fade - GROOVE_DEPTH * groove + MARGIN * outside * (1.0 - fade)
    # the waist: under the last crease the abdomen falls onto the head
    yb = y + BOW * x * x
    z -= NECK_DROP * sstep(CREASES[-1], CREASES[-1] - NECK_SPAN, yb)
    return z


def head_top(x, y):
    across = np.clip(1.0 - (np.abs(x) / HEAD_A) ** HEAD_P, 0.0, 1.0) ** 0.5
    rise = 0.45 + 0.55 * sstep(HEAD_RISE[0], HEAD_RISE[1], y)
    front = 1.0 - (1.0 - HEAD_FRONT[2]) * sstep(HEAD_FRONT[0], HEAD_FRONT[1], y)
    (cx, cy), (rx, ry), ch = CHEEK
    cheek = ch * np.exp(-((np.abs(x) - cx) / rx) ** 2 - ((y - cy) / ry) ** 2)
    d = slice_distance(x, y)
    bo, bh, bw = BROW
    brow = bh * np.exp(-((d - SLICE_R - bo) / bw) ** 2)
    z = HEAD_H * across * rise * front + cheek + brow
    z = z * sstep(-1.2, -3.6, y)             # (nothing of the head behind the waist)
    # the sockets: within a slice's rim the head lies under the rind's foot
    floor = SLICE_Z - 1.2 - SOCKET
    inside = sstep(SLICE_R + 0.4, SLICE_R - 0.4, d)
    return z * (1.0 - inside) + np.minimum(z, floor) * inside


def smooth_top(x, y):
    return smax(shell_top(x, y), head_top(x, y), 0.7)


def body_top(x, y, d):
    return np.maximum(smooth_top(x, y) + peel(x, y), 0.35)


def body_bottom(x, y, d):
    return np.full_like(x, -BELLY)


def body_rim(x, y):
    return np.zeros_like(x)


def light_value(base, solid, a=3.2, b=1.2):
    """A shade value from a normal: base where it faces straight up, more towards the sun, less away and down. The
    normal is the surface's without the peel's dimples (its rim rounded as Solid.shape rounds it), so that the bands
    follow the plates and the rim, not the dimples."""
    L = np.array(tuple(LIGHT))

    def rounded(x, y):
        d = np.minimum(solid.dist(x, y), EDGE_ROUND)
        return smooth_top(x, y) * np.sqrt(np.maximum(0.0, d * (2 * EDGE_ROUND - d))) / EDGE_ROUND

    def fn(x, y, z, n):
        h = 0.05
        zx = (rounded(x + h, y) - rounded(x - h, y)) / (2 * h)
        zy = (rounded(x, y + h) - rounded(x, y - h)) / (2 * h)
        ns = np.stack([-zx, -zy, np.ones_like(zx)], axis=1)
        ns /= np.linalg.norm(ns, axis=1)[:, None]
        under = (z < -0.05)[:, None]
        n = np.where(under, n, ns)
        value = base + a * (n @ L - FLAT) + b * (n[:, 2] - 1.0)
        _, crease, lip = plate_profile(x, y)
        groove, _ = groove_profile(x, y)
        fade = sstep(PLATE_FADE[1], PLATE_FADE[0], np.abs(x)) * (y > CREASES[-1] - 0.5)
        return value - 1.1 * crease * fade + LIP_LIGHT[1] * lip * fade - 1.0 * groove
    return fn


def body_lines():
    """The lines the body's mesh follows: along each crease (its bottom, the middle of its drop, the lip's top, the
    lip's light band), the groove (its middle and sides), the waist, round the sockets and their brows."""
    out = []
    xs = np.arange(-14.4, 14.41, 0.7)
    for upper, lower in zip(CREASES, CREASES[1:]):
        span = upper - lower
        for frac in (0.0, 0.5 * LIP, LIP, LIP + LIP_LIGHT[0]):
            out.append([(float(x), float(lower + frac * span - BOW * x * x)) for x in xs])
    (gx, gy), ga, gb, gp = GROOVE
    ys = np.arange(GROOVE_Y[0] - 0.5, GROOVE_Y[1] + 0.51, 0.7)
    for side in (-1, 1):
        for off in (-GROOVE_W, 0.0, GROOVE_W):
            pts = []
            for y in ys:
                dy = min(1.0, abs(y - gy) / gb)
                xg = ga * (1.0 - dy ** gp) ** (1.0 / gp)
                pts.append((side * (xg + off), float(y)))
            out.append(pts)
    xs = np.arange(-20.0, 20.01, 0.7)
    for dy in NECK_LINES:
        out.append([(float(x), float(CREASES[-1] - dy - BOW * x * x)) for x in xs])
    for side in (-1, 1):
        cx, cy = side * SLICE_C[0], SLICE_C[1]
        for r in SOCKET_LINES:
            n = int(2 * math.pi * r / 0.7)
            ring = [(cx + r * math.cos(2 * math.pi * i / n), cy + r * math.sin(2 * math.pi * i / n)) for i in range(n)]
            out.append(ring + [ring[0]])
    return out


# --- Materials ---------------------------------------------------------------------------------------------------------
# (key, palette index, metallic, roughness, emission strength in its own colour)
MATS = [
    (0x7a, 0x7a, 0.15, 0.34, 0.07), (0x7b, 0x7b, 0.15, 0.3, 0.09), (0x7c, 0x7c, 0.15, 0.28, 0.11),
    (0x7d, 0x7d, 0.15, 0.26, 0.13), (0x7e, 0x7e, 0.12, 0.24, 0.15),
    ("rind", 0x7c, 0.1, 0.22, 0.14), ("pith", 0x7e, 0.0, 0.5, 0.16), ("membrane", 0x7f, 0.0, 0.3, 0.26),
    ("juice", 0x7d, 0.0, 0.12, 0.36), ("crest", 0x7e, 0.0, 0.1, 0.44), ("core", 0x7f, 0.0, 0.2, 0.32),
]
# The shades the body and the limbs are painted in, by their light value (lowest value, key).
BODY_BANDS = [(-99, 0x7b), (5.65, 0x7c), (6.55, 0x7d)]
LIMB_BANDS = [(-99, 0x7a), (4.5, 0x7b), (5.65, 0x7c), (6.5, 0x7d), (7.1, 0x7e)]
BODY_LIGHT = 6.4
LIMB_LIGHT = 6.35
INNER_DARK = 1.3                     # the limbs' inner sides this much darker


def materials():
    pal = k.level_palette()
    m = {}
    for key, index, metallic, roughness, glow in MATS:
        name = key if isinstance(key, str) else "%02x" % key
        m[key] = k.material(f"lemon_{name}", palette=index, metallic=metallic, roughness=roughness,
                            emission=pal[index], emission_strength=glow)
    return m


# --- The body ----------------------------------------------------------------------------------------------------------

def body_zone(x, y):
    """The colour a face of the body takes by where it lies on the plates (its middle; the zones' borders are lines of
    the mesh): the deep part of a crease's drop 0x7a, its upper part 0x7b, the lip's top 0x7d, the waist 0x7a and
    0x7b under it; None elsewhere (painted by its light)."""
    if abs(x) < PLATE_FADE[0] + 0.6:
        yb = y + BOW * x * x
        for upper, lower in zip(CREASES, CREASES[1:]):
            w = (yb - lower) / (upper - lower)
            if 0.0 <= w < 0.5 * LIP:
                return 0x7a
            if 0.5 * LIP <= w < LIP:
                return 0x7b
            if LIP <= w < LIP + LIP_LIGHT[0]:
                return 0x7d
    yb = y + BOW * x * x
    if CREASES[-1] - NECK_LINES[0] <= yb < CREASES[-1] and abs(x) < 17.0:
        return 0x7a
    if CREASES[-1] - NECK_LINES[1] <= yb < CREASES[-1] - NECK_LINES[0] and abs(x) < 17.0:
        return 0x7b
    return None


def paint_body(solid):
    """Zones by the plates (body_zone), the rest in bands of its light value (BODY_BANDS) cut along smooth contours; the
    underside 0x7b."""
    solid.field("light", light_value(BODY_LIGHT, solid))
    bm = solid.bm
    tops = [fc for fc in bm.faces if fc in solid.tops and fc.is_valid]
    keys, free = {}, set()
    for fc in tops:
        c = fc.calc_center_median()
        key = body_zone(c.x, c.y)
        if key is None:
            free.add(fc)
        else:
            keys[fc] = key
    for lowest, _ in BODY_BANDS[1:]:
        free = split_contour(bm, solid.vals, "light", lowest, free)
    for fc in free:
        value = sum(solid.vals["light"][v] for v in fc.verts) / len(fc.verts)
        key = BODY_BANDS[0][1]
        for lowest, k_ in BODY_BANDS:
            if value >= lowest:
                key = k_
        keys[fc] = key
    for fc in bm.faces:
        keys.setdefault(fc, 0x7b)
    solid.keys = keys


def body(m):
    f = BodyField("she", sigma=0.7)
    solid = LinedSolid(f, (-25.0, 25.0, -23.0, 24.5), GRID, body_lines())
    solid.shape(body_top, body_bottom, body_rim, radius=EDGE_ROUND, bottom_radius=BELLY_ROUND)
    paint_body(solid)
    obj = solid.finish("body", m)
    obj["cap"] = 0x7c
    return obj


# --- The slices --------------------------------------------------------------------------------------------------------
# Rings of the slice's polar mesh, from its middle out and down its rind's wall: (radius, height over its face); the
# bands between them: the core, the juice (the segments and the membranes between them, by the spoke field), the pith,
# the rind.
SLICE_RINGS = [(0.0, 0.26), (0.62, 0.22), (1.5, 0.26), (2.5, 0.32), (3.5, 0.34), (4.5, 0.32), (5.3, 0.26), (5.9, 0.12),
               (6.3, 0.1), (6.55, 0.22), (6.9, 0.32), (7.25, 0.2), (7.44, -0.15), (7.47, -1.0), (7.2, -1.55)]
BAND_PARTS = ["core"] + ["juice"] * 6 + ["pith"] + ["rind"] * 6
JUICE_R = (0.62, 5.9)
SLICE_SEGMENTS = 56
SPOKES = 8
SPOKE_TURN = 0.0                     # the first membrane's direction (degrees from +X)
SPOKE_W = (0.4, 0.28)                # the membranes' half-width at the core and at the pith
CUSHION = 0.34                       # how far a segment's middle rises over its membranes
CREST_AT = 0.62                      # a segment's crest: where its cushion is higher than this fraction


def spoke_distance(r, theta):
    """How far a point (r, theta) lies from the nearest membrane, less its half-width there (> 0 in a segment)."""
    step = 2 * math.pi / SPOKES
    a = (theta - math.radians(SPOKE_TURN)) % step
    off = min(a, step - a)
    hw = SPOKE_W[0] + (SPOKE_W[1] - SPOKE_W[0]) * min(1.0, max(0.0, r / 6.0))
    return r * math.sin(min(off, math.pi / 2)) - hw


def slice_obj(name, side, m):
    """A slice lying flat on the head (its face SLICE_Z high), its middle at (side * SLICE_C.x, SLICE_C.y)."""
    cx, cy = side * SLICE_C[0], SLICE_C[1]
    bm = bmesh.new()
    rings = []
    vals = {"spoke": {}, "cush": {}}
    for r, h in SLICE_RINGS:
        if r < 1e-6:
            v = bm.verts.new((cx, cy, SLICE_Z + h))
            rings.append([v])
            vals["spoke"][v] = -1.0
            continue
        ring = []
        for j in range(SLICE_SEGMENTS):
            theta = 2 * math.pi * j / SLICE_SEGMENTS
            v = bm.verts.new((cx + r * math.cos(theta), cy + r * math.sin(theta), SLICE_Z + h))
            ring.append(v)
            vals["spoke"][v] = spoke_distance(r, theta)
        rings.append(ring)
    band_of = {}
    for i in range(len(rings) - 1):
        a, b = rings[i], rings[i + 1]
        for j in range(SLICE_SEGMENTS):
            jn = (j + 1) % SLICE_SEGMENTS
            f = bm.faces.new((a[0], b[j], b[jn]) if len(a) == 1 else (a[j], b[j], b[jn], a[jn]))
            band_of[f] = i
    # the bottom: a flat cap under the rind's foot
    last = rings[-1]
    bottom = bm.verts.new((cx, cy, SLICE_Z + SLICE_RINGS[-1][1]))
    vals["spoke"][bottom] = -1.0
    for j in range(SLICE_SEGMENTS):
        band_of[bm.faces.new((last[(j + 1) % SLICE_SEGMENTS], last[j], bottom))] = len(BAND_PARTS) - 1
    # the segments' cushions (on the juice rings): their middles higher than their membranes
    for v in bm.verts:
        r = math.hypot(v.co.x - cx, v.co.y - cy)
        c = 0.0
        if JUICE_R[0] < r < JUICE_R[1] and v.co.z > SLICE_Z:
            edge = min(1.0, max(0.0, (r - JUICE_R[0]) / 0.8)) * min(1.0, max(0.0, (JUICE_R[1] - 0.15 - r) / 0.6))
            c = edge * float(sstep(0.0, 1.1, vals["spoke"][v]))
            v.co.z += CUSHION * c
        vals["cush"][v] = c
    # cut along the membranes' borders and the crests' borders (the juice bands only)
    juice = {f for f, i in band_of.items() if BAND_PARTS[i] == "juice"}
    juice = split_contour(bm, vals, "spoke", 0.0, juice)
    split_contour(bm, vals, "cush", CREST_AT, juice)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    keys = []
    for f in bm.faces:
        c = f.calc_center_median()
        r = math.hypot(c.x - cx, c.y - cy)
        part = "rind"
        if c.z > SLICE_Z - 0.2:
            for i, ((r0, _), (r1, _)) in enumerate(zip(SLICE_RINGS, SLICE_RINGS[1:])):
                if r0 <= r <= r1:
                    part = BAND_PARTS[i]
                    break
        if part == "juice":
            sd = sum(vals["spoke"][v] for v in f.verts) / len(f.verts)
            cu = sum(vals["cush"][v] for v in f.verts) / len(f.verts)
            part = "membrane" if sd < 0 else ("crest" if cu > CREST_AT else "juice")
        keys.append(part)
    mesh = bpy.data.meshes.new(name)
    slots = []
    for key in keys:
        if key not in slots:
            slots.append(key)
    for f, key in zip(bm.faces, keys):
        f.material_index = slots.index(key)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    for key in slots:
        mesh.materials.append(m[key])
    k.smooth(obj, 50)
    obj["cap"] = "juice"
    return obj


# --- The forceps and the mandibles -------------------------------------------------------------------------------------
# The left ones, from their roots in the body to their points: (x, y, z, half-width across the path in plan,
# half-height); the right ones are their mirror images.
CERCUS = [(-10.7, 18.6, 3.0, 3.3, 1.9), (-10.65, 22.0, 3.45, 3.45, 2.2), (-10.55, 26.0, 3.8, 3.5, 2.3),
          (-10.45, 30.0, 4.05, 3.5, 2.25), (-10.0, 32.6, 4.15, 3.4, 2.15), (-9.1, 34.8, 4.15, 3.15, 2.0),
          (-7.9, 36.8, 4.05, 2.85, 1.8), (-6.5, 38.5, 3.85, 2.5, 1.55), (-4.9, 40.0, 3.6, 2.05, 1.25),
          (-3.1, 41.0, 3.35, 1.5, 0.9), (-1.7, 41.55, 3.2, 0.85, 0.5), (-0.8, 41.85, 3.1, 0.12, 0.08)]
MANDIBLE = [(-20.6, -12.2, 2.5, 2.7, 1.7), (-20.0, -16.0, 2.65, 3.4, 2.0), (-18.6, -19.4, 2.6, 4.5, 2.2),
            (-17.3, -22.2, 2.5, 4.7, 2.15), (-16.4, -24.8, 2.4, 4.0, 2.0), (-15.7, -28.0, 2.3, 3.5, 1.85),
            (-15.25, -31.5, 2.2, 3.2, 1.7), (-14.6, -34.6, 2.1, 3.05, 1.55), (-13.5, -37.2, 2.0, 2.8, 1.4),
            (-11.9, -39.2, 1.9, 2.25, 1.15), (-10.3, -40.6, 1.8, 1.55, 0.85), (-9.0, -41.5, 1.75, 0.8, 0.5),
            (-8.2, -42.0, 1.7, 0.12, 0.1)]
LIMB_POWER = 2.0
LIMB_SEGMENTS = 16


def mirrored(stations):
    return [(-st[0],) + tuple(st[1:]) for st in stations]


def paint_limb(obj, m, side):
    """band_split by how the limb's vertices face the sun and up (light_value), its inner side (towards the
    beetle's middle) darker."""
    mesh = obj.data
    L = Vector(LIGHT)
    values = []
    for v in mesh.vertices:
        n = Vector(v.normal)
        inner = max(0.0, -side * n.x)          # the left limb's inner side faces +x
        values.append(LIMB_LIGHT + 3.2 * (n.dot(L) - FLAT) + 1.2 * (n.z - 1.0) - INNER_DARK * inner)
    band_split(obj, values, [(lo, m[key]) for lo, key in LIMB_BANDS])
    k.smooth(obj, 80)
    return obj


def limbs(m):
    out = []
    for name, stations in (("cercus", CERCUS), ("mandible", MANDIBLE)):
        for side in (-1, 1):
            st = stations if side < 0 else mirrored(stations)
            obj = tube(f"{name}{side:+d}", [s + (LIMB_POWER,) for s in st], m[0x7c], segments=LIMB_SEGMENTS)
            paint_limb(obj, m, side)
            obj["cap"] = 0x7c
            out.append(obj)
    return out


# --- The whole, its checks and its pieces ------------------------------------------------------------------------------

def build_whole():
    k.reset()
    m = materials()
    parts = [body(m), slice_obj("slice_l", -1, m), slice_obj("slice_r", 1, m)] + limbs(m)
    for obj in parts:
        mk.apply(obj)
    triangulate(parts)
    bpy.context.view_layer.update()
    return parts, m


def shear_to_camera(objects):
    """Moves every point of the picture's plane along the game camera's line of sight to its height (y - z tan T), so
    that the camera sees each where the sprite draws it; the normals follow (the shear's inverse transpose)
    (polish_lava_grub.py's)."""
    for obj in objects:
        mesh = obj.data
        normals = [Vector(cn.vector) for cn in mesh.corner_normals]
        for v in mesh.vertices:
            v.co.y -= v.co.z * TAN_T
        out = [Vector((n.x, n.y, n.z + TAN_T * n.y)).normalized() for n in normals]
        mesh.normals_split_custom_set([tuple(n) for n in out])
        mesh.update()


# name, sprite, box (x0, x1, y0, y1) in the picture's plane
PIECES = [("lemon_beetle_tl", 16, (-24.0, 0.0, 14.0, 42.0)), ("lemon_beetle_tr", 18, (0.0, 24.0, 14.0, 42.0)),
          ("lemon_beetle_ml", 54, (-24.0, 0.0, -14.0, 14.0)), ("lemon_beetle_mr", 56, (0.0, 24.0, -14.0, 14.0)),
          ("lemon_beetle_bl", 92, (-24.0, 0.0, -42.0, -14.0)), ("lemon_beetle_br", 94, (0.0, 24.0, -42.0, -14.0))]
LAYOUT = [[16, 18], [54, 56], [92, 94]]


def whole_mask(sheet):
    mask = [[False] * W for _ in range(H)]
    for r0, row in enumerate(LAYOUT):
        for c0, sprite in enumerate(row):
            for r, line in enumerate(k.sprite_mask(sheet, sprite)):
                for c, v in enumerate(line):
                    if v:
                        mask[r0 * 28 + r][c0 * 24 + c] = True
    return mask


def build():
    options = k.args()
    out = mk.outdir(options)
    only = options["only"].split(",") if "only" in options else None
    sheet = None
    if "check" in options:
        sheets = options["check"]
        sheet = os.path.join(sheets, "enemy_x27.png") if os.path.isdir(sheets) else sheets
    whole, m = build_whole()
    low, high = mk.bounds(whole)
    print("== whole: %d triangles, %d materials, x %.2f..%.2f y %.2f..%.2f z %.2f..%.2f" % (
        mk.triangles(whole), len(mk.materials_of(whole)), low.x, high.x, low.y, high.y, low.z, high.z))
    mask = whole_mask(sheet) if sheet else None
    if sheet:
        mk.compare("whole, as the camera sees it", mk.coverage(whole, W, H), mask)
    if "whole" in options or "preview" in options or sheet:
        seen = []
        for o in whole:
            c = o.copy()
            c.data = o.data.copy()
            bpy.context.scene.collection.objects.link(c)
            seen.append(c)
        shear_to_camera(seen)
        for o in whole:
            o.hide_render = True
        if sheet:
            mk.compare("whole, from straight above", mk.coverage(seen, W, H), mask)
        if "whole" in options:
            mk.export(seen, options["whole"])
        if "preview" in options:
            bpy.context.scene.view_settings.view_transform = "Standard"
            mk.preview(options["preview"] + "lemon_beetle", seen, size=(W, H), scale=8, distance=1.7)
        for o in seen:
            mesh = o.data
            bpy.data.objects.remove(o)
            bpy.data.meshes.remove(mesh)
        for o in whole:
            o.hide_render = False
    bpy.context.view_layer.update()
    for name, sprite, box in PIECES:
        if only and name not in only:
            continue
        parts = [p for p in (cut(src, box, m[src["cap"]]) for src in whole) if p is not None]
        drop_unused(parts)
        shear_to_camera(parts)
        mk.transform(parts, Matrix.Translation((-(box[0] + box[1]) / 2, -(box[2] + box[3]) / 2, 0)))
        bpy.context.view_layer.update()
        triangulate(parts)
        if "stats" in options:
            for obj in sorted(parts, key=lambda o: -mk.triangles([o])):
                print("    %-14s %6d" % (obj.name, mk.triangles([obj])))
        parts = [join(parts, name)]
        parts[0].data.name = name
        for src in whole:
            src.hide_render = True
        if sheet:
            mk.compare("%s (x27 %d), from straight above" % (name, sprite), mk.coverage(parts, 24, 28),
                       k.sprite_mask(sheet, sprite))
        mk.report(name, parts, os.path.join(out, name + ".glb"))
        if "preview" in options and options.get("pieces") == "1":
            mk.preview(options["preview"] + name, parts)
        for obj in parts:
            bpy.data.objects.remove(obj)
        for src in whole:
            src.hide_render = False


if __name__ == "__main__":
    build()
