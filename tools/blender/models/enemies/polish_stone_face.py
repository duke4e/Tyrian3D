"""The stone face lying on the ground of ASTEROID1 and ASTEROID2, polished (2026-10-22, round 30; it replaces
wave3_j_rocks.py's stone face, a pillow inflated over the outline with gaussian features, wave3_ap_face.py's damaged
left half and wave3_ao_works.py's damaged right half). One 48 x 56 picture that the game puts together from four 2x2
sprites of two sheets: top left D 155, top right P 123, bottom left D 165, bottom right P 127; and its damaged look,
D 163, P 125 above D 167, P 129.

PLACEMENT (the level events, tools/content/tyrevents.py; the enemy data, tools/content/tyrdata.py)

Four enemies (episodes 1-3 and 5, the same data): 575 (D 155), 576 (P 123), 573 (D 165), 574 (P 127), armour 25 each,
worth 50 each, one frame, not animated, no launches. The levels send them by event 12 ("4-part enemy": 573 at (x, y),
574 at (x + 24, y), 575 at (x, y - 28), 576 at (x + 24, y - 28): the picture whole, as the sheets lay it out) on the
ground2 layer (d6 4): ASTEROID1 at t6068, ASTEROID2 at t1084, 1616, 1750, 6012, 6824 (two), 6880 and 7244, every time
the four with one link number. Damage: dgr 163, 125, 167, 129 with dlevel 10 (D 155 -> 163, P 123 -> 125, D 165 ->
167, P 127 -> 129); a hit that takes a piece to 10 or less switches every enemy with its link and a dlevel to its
damaged sprite (tyrian2.c), so the four always switch together, and shot, the four die together and leave the
game's slumped wrecks of the damaged models (tyrian2.c leave_wreck). No episode 6 level places it (GREY MOON and
VAULT take only ASTEROID2's boss block, link 45). No other enemy shows these sprites (catalog.json, launched enemies
too); none is another sprite's pixels mirrored, turned or in other ramps (twins.py): no frame models, no twins.
ASTEROID1's and ASTEROID2's terrain is flat with holes (tools/terrain/levels.json): height=-4 sets the face on it.

THE FACE

As the sprites and their 4x upscales draw it (columns and rows of the picture; all of it in the grey ramp 0, 0x01-0x0d):
a stone face lying on its back, the crown up the screen, an oval 29 pixels wide (columns 10-38, its axis the middle of
column 24) and 49 long (rows 3-51), rimmed in near black (the head's sides falling away); the crown dark (0x04-0x07);
a broad high forehead (0x09, rows 8-21) lit along its left edge (0x0a-0x0d); a heavy brow lit along its top (rows
19-21); two deep dark sockets under it (0x01-0x03, columns 15-23 and 25-35 of rows 22-28), the eyes shut in them; a
long straight nose down the axis (rows 22-34), its left flank lit (0x09-0x0d), its right in shadow, the nostrils dark
under its tip (row 35); cheekbones lit either side (columns 15-19 and 30-33 of rows 29-34); full lips (the upper lip
lit, rows 37-39; the mouth a dark line, row 40; the lower lip, row 41), a groove under them, a rounded chin (rows
44-47) and the jaw narrowing to its point (row 51).

Built as such a carved face of the asteroid levels' stone: one closed heightfield over the outline (traced through
the middles of the sprite's rows' outer edges, smoothed along its length, SMOOTH, and grown GROW so that it covers the
edge pixels; a grid GRID apart cut along it with polish_coral_manta.split_contour), its underside flat a little under
the ground (SKIRT); the surface a mask's: its sides falling steeply to the ground over the outline's last RIM pixels,
the face's front plane over them (PLANE, falling away across the face, CURVE) and the features modelled on it with
smooth bumps and hollows (BUMPS: the forehead's broad boss, the brow ridge, the sockets and the shut lids in them, the
nose's bridge, ridge, tip and wings, the nostrils, the cheekbones and the gaunt hollows under them, the temples, the
lips, the mouth and its corners, the groove under the lips, the chin and the folds from the nose to the mouth), 9.1
high at the nose's tip, 6.8 at the forehead, 6 over the cheekbones. Designed in the game camera's view (20 degrees
from straight down, from the bottom of the screen): every point is placed TILT * z down the screen from where the
sprite draws it, so that the camera sees each feature where the sprite has it (as polish_dark_orb.py paints its
face); seen from straight above the nose's tip lies 3.3 pixels lower. Weathered as the asteroids are
(polish_asteroids.roughen's smooth noise, gentler: WEATHER, a carved face). Painted by a value per point from how it
lies (shade_values(): the stone's middle grey and how much more or less of the sun it gets than a face looking up;
the features' tops lighter and the hollows darker by how far they lie over or under the face's plane; the rim falling
to the ground and the crown darker; the forehead's boss lighter, with a gleam along its left and lower edges where
the sprite lights it; the sockets dark all over; the lower cheeks gaunt), banded into the sprite's greys 0x02-0x0a
(BANDS) along smooth contours (polish_orb_red.band_split).

The damaged look (D 163, P 125 above D 167, P 129: their pixels darker than the intact ones along thin lines, lighter
beside them): cracks split the stone, across the crown (rows 4-9) and the forehead from the left temple to the
middle and on down to the brow, from the crown down over the right eye to the right temple, down the left edge,
down the left side of the nose from the left eye, across the right cheek, down the left cheek and jaw to the chin and
down the right jaw (CRACKS, traced from the differences, their courses wandering a little off them, WANDER). Each
crack a V-shaped groove cut into the stone (CRACK_DEPTH deep, CRACK_HALF wide either side, varying along it and
narrower at its ends), the chips beside them (CHIPS: the sprite's lighter pixels) shallow flakes broken off
(CHIP_DEPTH); painted over the bands along their contours (sharp borders): the cracks near black (0x02, their walls
shaded by the light), the chips fresh, lighter stone (0x0a). The rest is the intact face's, so that a damaged piece
meets an intact one (the four switch together anyway).

Each look is built whole and cut along the planes the camera sees as the sprites' edges (view_cut(): x = 0 upright, y +
TILT z = 0 leaning back up the screen, so that each piece holds what the camera sees in its sprite; the cuts capped
with the stone's inside, 0x05, the faces' own winding kept, the uncut face's shading) into its four pieces, each moved
so that its sprite's centre is its origin, every mesh triangulated (polish_k_pod.triangulate).

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up from the ground (z 0); the whole's
origin is the corner where the four sprites meet (pixel corner 24, 28 of the picture): column c is x = c + 0.5 - 24,
row r is y = 27.5 - r. The pieces' centres: 155 (-12, 14), 123 (12, 14), 165 (-12, -14), 127 (12, -14).

models.cfg: the model lines stay (stone_face_tl / _tr / _bl / _br, stone_face_tl_damaged / _bl_damaged,
stone_face_dmg_tr / _br, all origin); the sprite lines of D 155, P 123, D 165, P 127, D 163, P 125, D 167 and P 129
get height=-4 (the face lies on the terrain). Replaces wave3_j_rocks.py's stone face (its "D 155, P 123, D 165, P 127:
the stone face" section: gauss(), stone_face_whole(), stone_face_piece() and the four model registrations, its
stone_face_* docstring paragraph and "[--whole stone_face ...]" in its usage), wave3_ap_face.py (all of it) and
wave3_ao_works.py's "P 125 129: the stone face, cracked" section (face_frames(), stone_face_cracked() and its two
model registrations, its stone_face_dmg bullet and "the stone face's damaged look" in its docstring, rocks =
kit.quiet_import("wave3_j_rocks")); and the pixels only those read: wave3_j_art.py's FACE, wave3_ap_art.py's FACE_DMG,
wave3_ao_art.py's FACE_DMG.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouettes as the game's
camera sees them, of each look's whole and of each piece, against the sprites' pixels), --preview <prefix> (each
piece's top and 3/4 views), --whole <prefix> (each look's uncut face as <prefix>stone_face[_damaged].glb), --only
<model,...>, --looks intact,damaged (default both).
"""
import math
import os
import sys

import bmesh
import bpy
import mathutils.noise as noise
import numpy as np
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k  # noqa: E402
from polish_coral_manta import split_contour  # noqa: E402
from polish_deli_boss import join, drop_unused  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402
from polish_orb_red import band_split  # noqa: E402

AXIS = 0.5                                   # the face's mirror axis: the middle of the picture's column 24
GRID = 0.6                                   # the heightfield's grid (pixels)
SKIRT = -0.8                                 # the underside, a little under the ground
TILT = math.tan(math.radians(20.0))          # the camera shows a point this much further up the screen per pixel up
LIGHT = Vector((-0.6, 0.6, 1.0)).normalized()   # towards the game's sun (render_gpu.c: from above and the top left)

# The pieces: name (intact, damaged), sprite (intact, damaged), box (x0, x1, y0, y1) in the whole's coordinates.
PIECES = [(("stone_face_tl", "stone_face_tl_damaged"), ("D 155", "D 163"), (-24.0, 0.0, 0.0, 28.0)),
          (("stone_face_tr", "stone_face_dmg_tr"), ("P 123", "P 125"), (0.0, 24.0, 0.0, 28.0)),
          (("stone_face_bl", "stone_face_bl_damaged"), ("D 165", "D 167"), (-24.0, 0.0, -28.0, 0.0)),
          (("stone_face_br", "stone_face_dmg_br"), ("P 127", "P 129"), (0.0, 24.0, -28.0, 0.0))]

# The outline: each row of the picture, its first and last column (the sprite's pixels, symmetric about column 24).
ROWS = {3: (20, 28), 4: (18, 30), 5: (17, 31), 6: (16, 32), 7: (15, 33), 8: (14, 34), 9: (13, 35), 10: (12, 36),
        11: (11, 37), 12: (11, 37), **{r: (10, 38) for r in range(13, 30)}, 30: (11, 37), 31: (11, 37), 32: (11, 37),
        33: (12, 36), 34: (12, 36), 35: (12, 36), 36: (13, 35), 37: (13, 35), 38: (13, 35), 39: (13, 35),
        40: (14, 34), 41: (14, 34), 42: (14, 34), 43: (15, 33), 44: (15, 33), 45: (16, 32), 46: (17, 31),
        47: (18, 30), 48: (19, 29), 49: (20, 28), 50: (21, 27), 51: (22, 26)}


def Y(r):
    """A row's middle."""
    return 27.5 - r


# --- The outline ------------------------------------------------------------------------------------------------------

def outline():
    """The outline in the camera's view (counter-clockwise from above): through the middles of the rows' outer edges
    and along the top and bottom rows' outer edges, resampled evenly and smoothed along its length (a gaussian
    SMOOTH pixels wide, which takes out the rows' steps), a little out (GROW) so that it covers the edge pixels."""
    rows = sorted(ROWS)
    right = [(ROWS[r][1] + 1 - 24.0, Y(r)) for r in rows]
    left = [(ROWS[r][0] - 24.0, Y(r)) for r in rows]
    top, bottom = rows[0], rows[-1]
    foot = 28.0 - bottom - 1.0
    pts = ([(ROWS[bottom][0] - 24.0 + 0.6, foot), (ROWS[bottom][1] + 1 - 24.0 - 0.6, foot)] + list(reversed(right)) +
           [(ROWS[top][1] + 1 - 24.0 - 0.6, 28.0 - top), (ROWS[top][0] - 24.0 + 0.6, 28.0 - top)] + left)
    p = np.array(pts)
    seg = np.linalg.norm(np.roll(p, -1, axis=0) - p, axis=1)
    s = np.concatenate([[0.0], np.cumsum(seg)])
    total = s[-1]
    n = int(total / 0.25)
    t = np.linspace(0.0, total, n, endpoint=False)
    closed = np.vstack([p, p[:1]])
    q = np.stack([np.interp(t, s, closed[:, 0]), np.interp(t, s, closed[:, 1])], axis=1)
    k_half = int(3 * SMOOTH / 0.25)
    w = np.exp(-0.5 * (np.arange(-k_half, k_half + 1) * 0.25 / SMOOTH) ** 2)
    w /= w.sum()
    sm = np.zeros_like(q)
    for i, wi in zip(range(-k_half, k_half + 1), w):
        sm += wi * np.roll(q, -i, axis=0)
    # out along the normal (the polygon runs counter-clockwise: out is to the right of its direction)
    tang = np.roll(sm, -1, axis=0) - np.roll(sm, 1, axis=0)
    tang /= np.linalg.norm(tang, axis=1)[:, None]
    normal = np.stack([tang[:, 1], -tang[:, 0]], axis=1)
    sm = sm + GROW * normal
    return [tuple(v) for v in sm[::2]]


SMOOTH = 0.9         # the outline's smoothing along its length (pixels)
GROW = 0.15          # and how far out it is moved


class Outline:
    """Signed distances (positive inside) to the outline, for arrays of points."""

    def __init__(self):
        p = np.array(outline())
        self.a = p
        self.b = np.roll(p, -1, axis=0)

    def distance(self, x, y):
        x, y = np.atleast_1d(np.asarray(x, float)), np.atleast_1d(np.asarray(y, float))
        out = np.empty(len(x))
        a, b = self.a, self.b
        dx, dy = b[:, 0] - a[:, 0], b[:, 1] - a[:, 1]
        ll = np.maximum(dx * dx + dy * dy, 1e-12)
        for s in range(0, len(x), 2048):
            px, py = x[s:s + 2048, None], y[s:s + 2048, None]
            t = np.clip(((px - a[:, 0]) * dx + (py - a[:, 1]) * dy) / ll, 0.0, 1.0)
            d2 = (px - a[:, 0] - t * dx) ** 2 + (py - a[:, 1] - t * dy) ** 2
            out[s:s + 2048] = np.sqrt(d2.min(axis=1))
        return out

    def inside(self, x, y):
        x, y = np.atleast_1d(np.asarray(x, float)), np.atleast_1d(np.asarray(y, float))
        out = np.empty(len(x), bool)
        a, b = self.a, self.b
        for s in range(0, len(x), 2048):
            px, py = x[s:s + 2048, None], y[s:s + 2048, None]
            cond = (a[:, 1] > py) != (b[:, 1] > py)
            den = np.where(b[:, 1] != a[:, 1], b[:, 1] - a[:, 1], 1e-12)
            xint = a[:, 0] + (py - a[:, 1]) * (b[:, 0] - a[:, 0]) / den
            out[s:s + 2048] = (cond & (px < xint)).sum(axis=1) % 2 == 1
        return out

    def signed(self, x, y):
        d = self.distance(x, y)
        return np.where(self.inside(x, y), d, -d)

    def nearest(self, x, y):
        a, b = self.a, self.b
        dx, dy = b[:, 0] - a[:, 0], b[:, 1] - a[:, 1]
        t = np.clip(((x - a[:, 0]) * dx + (y - a[:, 1]) * dy) / np.maximum(dx * dx + dy * dy, 1e-12), 0.0, 1.0)
        cx, cy = a[:, 0] + t * dx, a[:, 1] + t * dy
        i = int(np.argmin((x - cx) ** 2 + (y - cy) ** 2))
        return float(cx[i]), float(cy[i])


# --- The face's heights (in the camera's view) ------------------------------------------------------------------------

def sstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0.0, 1.0)
    return t * t * (3 - 2 * t)


def bump(u, y, cu, cy, su, sy, power=2.0):
    """A smooth bump (1 at its middle), su and sy its half-widths; power > 2 flattens its top."""
    q = np.abs((u - cu) / su) ** power + np.abs((y - cy) / sy) ** power
    return np.exp(-q)


# The face's front plane along its length (y: height), as the rows lie.
PLANE = [(-24.0, 3.4), (-21.0, 4.6), (-18.0, 5.3), (-13.0, 5.4), (-9.0, 5.5), (-5.0, 5.6), (0.0, 5.8), (5.0, 5.9),
         (10.0, 5.9), (15.0, 5.8), (19.0, 5.2), (22.0, 4.0), (25.0, 2.5)]
RIM = 5.0            # how far in from the outline the sides rise to the front plane (pixels)
CURVE = 0.016        # how much the front plane falls away across the face (per pixel squared from the axis)


def curve_np(points, v):
    xs = np.array([p[0] for p in points])
    ys = np.array([p[1] for p in points])
    return np.interp(v, xs, ys)


# The features: (weight, u, y, half-width across, half-width along, power, mirrored): bumps (+) and hollows (-) on the
# face's plane; mirrored ones come in pairs either side of the axis.
BUMPS = [
    # the forehead's broad boss, the brow ridge over each eye and the glabella between them
    (1.0, 0.0, 12.6, 7.6, 5.4, 2.8, False),
    (1.35, 5.0, 6.6, 4.4, 1.1, 2.0, True), (0.9, 0.0, 6.2, 2.0, 1.3, 2.0, False),
    # the sockets under the brow, deepest towards the nose, and the shut lids in them
    (-2.9, 5.1, 2.7, 4.0, 2.5, 2.3, True), (0.35, 5.0, 1.6, 2.4, 1.1, 2.0, True),
    # the nose: bridge, ridge and tip, the wings either side of the tip
    (1.1, 0.0, 3.0, 1.2, 3.2, 2.0, False), (2.5, 0.0, -2.4, 1.5, 3.6, 2.0, False),
    (2.4, 0.0, -5.7, 2.0, 1.6, 2.0, False), (1.2, 2.3, -6.3, 1.25, 1.05, 2.0, True),
    # the nostrils, and the face's plane under the nose
    (-1.0, 1.3, -7.5, 0.8, 0.5, 2.0, True), (-0.6, 0.0, -8.2, 2.4, 0.7, 2.0, False),
    # the cheekbones and the hollows under them
    (1.3, 7.4, -3.4, 3.0, 2.2, 2.0, True), (-1.5, 8.6, -10.6, 2.8, 3.6, 2.0, True),
    # the temples
    (-0.7, 11.6, 9.0, 2.4, 5.5, 2.0, True),
    # the lips, the mouth between them, its corners, the groove under them, the chin
    (1.1, 0.0, -10.6, 3.3, 1.2, 2.6, False), (-0.75, 0.0, -12.45, 3.0, 0.5, 2.0, False),
    (-0.55, 3.8, -12.3, 0.9, 0.9, 2.0, True), (1.1, 0.0, -13.7, 2.8, 0.9, 2.6, False),
    (-0.75, 0.0, -15.3, 2.8, 0.75, 2.0, False), (1.3, 0.0, -18.0, 3.0, 2.3, 2.0, False),
    # the folds from the nose's wings to the mouth's corners
    (-0.35, 4.0, -9.5, 0.7, 1.8, 2.0, True),
]


def features(x, y):
    """How far each point lies above (+) or under (-) the face's plane: the features alone."""
    x, y = np.atleast_1d(np.asarray(x, float)), np.atleast_1d(np.asarray(y, float))
    u = x - AXIS
    feat = np.zeros_like(x)
    for w, cu, cy, su, sy, pw, pair in BUMPS:
        feat += w * bump(u, y, cu, cy, su, sy, pw)
        if pair:
            feat += w * bump(u, y, -cu, cy, su, sy, pw)
    return feat


def height(x, y, damaged=False):
    """The face's top at arrays x, y (the camera's view), and how far inside the outline each point lies."""
    x, y = np.atleast_1d(np.asarray(x, float)), np.atleast_1d(np.asarray(y, float))
    d = np.maximum(SHAPE.signed(x, y), 0.0)
    u = x - AXIS
    t = np.clip(d / RIM, 0.0, 1.0)
    rise = 1.0 - (1.0 - t) ** 2.2                      # the sides: steep at the ground, rounding over to the plane
    plane = curve_np(PLANE, y) - CURVE * u * u
    z = SKIRT + (plane - SKIRT) * rise
    z = z + features(x, y) * sstep(0.5, 3.5, d)
    if damaged:
        depth, chips, _ = crack_field(x, y)
        z = np.maximum(z - CRACK_DEPTH * depth - CHIP_DEPTH * chips, np.minimum(z, SKIRT + 0.2))
    return z, d


def gradient(x, y, damaged=False):
    """The top's slopes (dz/dx, dz/dy) at arrays x, y, by differences."""
    h = 0.05
    gx = (height(x + h, y, damaged)[0] - height(x - h, y, damaged)[0]) / (2 * h)
    gy = (height(x, y + h, damaged)[0] - height(x, y - h, damaged)[0]) / (2 * h)
    return gx, gy


SHAPE = Outline()


# --- The damage -------------------------------------------------------------------------------------------------------
# The cracks (picture columns and rows of their courses), traced from the damaged sprites' pixels that are darker than
# the intact ones; their lips lighter where the sprites draw lighter pixels beside them.
CRACKS = [
    # across the crown
    [(17.0, 6.5), (19.0, 7.0), (20.5, 7.6), (22.5, 8.3), (24.5, 8.2), (26.0, 7.4), (27.5, 6.6), (28.5, 5.6),
     (30.0, 5.2)],
    # from the left temple across the forehead to the middle, and on down to the brow
    [(10.6, 13.2), (12.2, 14.0), (13.6, 15.2), (15.0, 16.2), (17.5, 16.5), (19.8, 17.0), (21.5, 17.8),
     (23.0, 18.3), (24.6, 18.1), (25.8, 17.2), (26.8, 16.2), (27.6, 14.6), (28.0, 12.6), (28.4, 10.6), (29.4, 9.3)],
    [(23.0, 18.3), (22.6, 19.6), (22.3, 21.0), (22.2, 22.4)],
    # from the crown down over the right eye to the right temple
    [(28.2, 12.2), (29.6, 12.4), (31.5, 12.8), (33.4, 11.6), (35.0, 10.6), (36.4, 9.8)],
    [(31.5, 12.8), (32.8, 14.6), (34.0, 16.4), (35.4, 17.4), (36.6, 18.6), (37.6, 20.0)],
    # the left edge, down from the temple
    [(11.4, 13.0), (11.8, 15.0), (12.5, 16.8), (13.0, 18.2), (12.2, 19.6), (11.4, 20.6)],
    # down the left side of the nose from the left eye
    [(19.0, 24.0), (20.5, 24.8), (21.8, 25.6), (22.6, 26.6), (23.0, 28.2), (23.6, 29.4), (24.4, 30.6),
     (24.8, 31.4)],
    # across the right cheek
    [(36.6, 26.2), (35.4, 27.2), (34.0, 28.0), (32.6, 29.0), (31.0, 29.8), (29.6, 30.4)],
    # down the left cheek and jaw to the chin
    [(13.2, 35.2), (15.0, 35.8), (16.6, 36.6), (17.8, 37.6), (18.8, 38.6), (19.2, 39.6), (18.6, 40.6),
     (18.8, 42.0), (19.4, 43.4), (20.6, 44.6), (21.2, 45.8), (20.8, 47.0), (21.2, 48.2)],
    # down the right jaw
    [(31.2, 36.2), (32.6, 37.2), (33.8, 38.2), (34.8, 39.4), (33.2, 39.8), (32.2, 40.6), (31.6, 41.6),
     (31.2, 43.0), (30.8, 44.6), (30.6, 46.0), (30.4, 47.2)],
]
# The chips: the damaged sprites' pixels lighter than the intact ones (columns, rows), beside the cracks.
CHIPS = [(20, 5), (23, 6), (24, 6), (20, 7), (21, 7), (22, 7), (23, 7), (29, 8), (20, 9), (21, 9), (22, 9), (23, 9),
         (29, 9), (29, 10), (30, 13), (31, 13), (32, 13), (33, 13), (34, 13), (30, 14), (31, 14), (26, 16), (27, 16),
         (15, 17), (16, 17), (17, 17), (18, 17), (14, 18), (13, 19), (23, 19), (12, 20), (21, 24), (33, 29), (22, 30),
         (23, 30), (30, 30), (23, 31), (24, 31), (29, 31), (15, 37), (16, 38), (32, 39), (31, 40), (30, 41), (30, 43),
         (21, 45), (20, 46)]
CRACK_DEPTH = 1.1    # the grooves' depth at their middles
CRACK_HALF = 0.6     # their half-width (varying along them by up to CRACK_VARY of it, narrower at their ends)
CRACK_VARY = 0.35
WANDER = (0.32, 0.7)  # how far a crack's course wanders off its polyline (pixels) and how fast (cycles per pixel)
CHIP_DEPTH = 0.35    # how deep the chips' flakes are broken off


def crack_courses():
    """Each crack's course: its polyline resampled every 0.25 pixels, each point moved off it along its normal by
    smooth noise (the crack's own), with its half-width there."""
    out = []
    for n, line in enumerate(CRACKS):
        p = np.array([(c + 0.5 - 24.0, 27.5 - r) for c, r in line])
        seg = np.linalg.norm(p[1:] - p[:-1], axis=1)
        s = np.concatenate([[0.0], np.cumsum(seg)])
        t = np.linspace(0.0, s[-1], max(2, int(s[-1] / 0.25) + 1))
        q = np.stack([np.interp(t, s, p[:, 0]), np.interp(t, s, p[:, 1])], axis=1)
        tang = np.gradient(q, axis=0)
        tang /= np.maximum(np.linalg.norm(tang, axis=1)[:, None], 1e-9)
        normal = np.stack([-tang[:, 1], tang[:, 0]], axis=1)
        off = np.array([noise.noise(Vector((tt * WANDER[1], 7.3 * n + 1.1, 0.5))) for tt in t])
        q = q + normal * (WANDER[0] * off)[:, None]
        vary = np.array([noise.noise(Vector((tt * 0.45, 3.1 * n + 9.7, 2.5))) for tt in t])
        ends = np.minimum(1.0, np.minimum(t, s[-1] - t) / 1.6)
        half = CRACK_HALF * (1.0 + CRACK_VARY * vary) * (0.45 + 0.55 * ends)
        out.append((q, half))
    return out


COURSES = crack_courses()


def crack_field(x, y):
    """(the cracks' groove depth share 0-1, the chips' share 0-1, the distance to the nearest crack) at arrays."""
    x, y = np.atleast_1d(np.asarray(x, float)), np.atleast_1d(np.asarray(y, float))
    depth = np.zeros(len(x))
    best = np.full(len(x), 1e9)
    px, py = x[:, None], y[:, None]
    for q, half in COURSES:
        a, b = q[:-1], q[1:]
        ha, hb = half[:-1], half[1:]
        dx, dy = b[:, 0] - a[:, 0], b[:, 1] - a[:, 1]
        ll = np.maximum(dx * dx + dy * dy, 1e-12)
        for s0 in range(0, len(x), 1024):
            sx, sy = px[s0:s0 + 1024], py[s0:s0 + 1024]
            t = np.clip(((sx - a[:, 0]) * dx + (sy - a[:, 1]) * dy) / ll, 0.0, 1.0)
            d = np.hypot(sx - (a[:, 0] + t * dx), sy - (a[:, 1] + t * dy))
            h = ha + (hb - ha) * t
            share = np.clip(1.0 - d / h, 0.0, 1.0).max(axis=1)
            depth[s0:s0 + 1024] = np.maximum(depth[s0:s0 + 1024], share)
            best[s0:s0 + 1024] = np.minimum(best[s0:s0 + 1024], d.min(axis=1))
    chips = np.zeros(len(x))
    for c, r in CHIPS:
        cx, cy = c + 0.5 - 24.0, 27.5 - r
        chips = np.maximum(chips, np.exp(-(np.hypot(x - cx, y - cy) / 0.56) ** 4))
    chips = chips * (depth < 0.05)
    return depth ** 1.2, chips, best


# --- The mesh -------------------------------------------------------------------------------------------------------

def face_mesh(damaged):
    """The face as a closed bmesh in the camera's view (z its heights; moved down the screen after): a grid over the
    outline, cut along it, its top at height() (the cracks cut in when damaged), its underside flat at SKIRT. Returns
    the bmesh and each vertex's kind (0 the top, 1 the rim along the outline, 2 the underside)."""
    x0, x1, y0, y1 = -15.0, 16.0, -25.0, 26.0
    nx, ny = int(math.ceil((x1 - x0) / GRID)), int(math.ceil((y1 - y0) / GRID))
    xs = [AXIS + (i - nx / 2) * GRID for i in range(nx + 1)]
    ys = [y0 + j * GRID for j in range(ny + 1)]
    X, Yg = np.meshgrid(np.array(xs), np.array(ys))
    sd = SHAPE.signed(X.ravel(), Yg.ravel()).reshape(X.shape)
    bm = bmesh.new()
    verts = {}
    for j in range(len(ys)):
        for i in range(len(xs)):
            if sd[j, i] > -2.0 * GRID:
                verts[i, j] = bm.verts.new((xs[i], ys[j], 0.0))
    for j in range(len(ys) - 1):
        for i in range(len(xs) - 1):
            corner = [(i, j), (i + 1, j), (i + 1, j + 1), (i, j + 1)]
            if not all(c in verts for c in corner) or max(sd[c[1], c[0]] for c in corner) <= 0:
                continue
            a, b, c, e = (verts[q] for q in corner)
            if (xs[i] + GRID / 2 < AXIS) == ((i + j) % 2 == 0):   # diagonals mirrored about the axis
                bm.faces.new((a, b, c))
                bm.faces.new((a, c, e))
            else:
                bm.faces.new((a, b, e))
                bm.faces.new((b, c, e))
    sdv = {}
    for v in bm.verts:
        dv = float(SHAPE.signed([v.co.x], [v.co.y])[0])
        if abs(dv) < 0.3 * GRID:  # onto the outline: no slivers along it
            v.co.x, v.co.y = SHAPE.nearest(v.co.x, v.co.y)
            dv = 0.0
        sdv[v] = dv
    split_contour(bm, {"sd": sdv}, "sd", 0.0)
    gone = [f for f in bm.faces if sum(sdv[v] for v in f.verts) / len(f.verts) < 0]
    bmesh.ops.delete(bm, geom=gone, context="FACES")
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
    top_faces = list(bm.faces)
    rim = {v for v in bm.verts if sdv[v] <= 1e-6}
    inner = [v for v in bm.verts if v not in rim]
    px = np.array([v.co.x for v in inner])
    py = np.array([v.co.y for v in inner])
    z, _ = height(px, py, damaged)
    for v, zz in zip(inner, z):
        v.co.z = float(zz)
    for v in rim:
        v.co.z = SKIRT
    kind = {v: 0 for v in inner}
    kind.update({v: 1 for v in rim})
    # the underside: the top's faces again, flat, reversed (the rim shared)
    under = {v: bm.verts.new((v.co.x, v.co.y, SKIRT)) for v in inner}
    kind.update({w: 2 for w in under.values()})
    for v in rim:
        under[v] = v
    bottom = []
    for f in top_faces:
        if all(v in rim for v in f.verts):
            continue
        bottom.append(bm.faces.new([under[v] for v in reversed(f.verts)]))
    bottom_set = set(bottom)
    inner_edges = [e for e in {e for f in bottom for e in f.edges}
                   if all(fc in bottom_set for fc in e.link_faces) and not all(v in rim for v in e.verts)]
    bmesh.ops.dissolve_limit(bm, angle_limit=math.radians(2.0), verts=[], edges=inner_edges, delimit={"NORMAL"})
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
    return bm, kind


def weather(bm, kind, seed):
    """The stone weathered: the top's points moved along their normals by smooth noise (the asteroids' roughen,
    gentler: a carved face), the rim and the underside kept."""
    bm.normal_update()
    shift = Vector((seed * 2.1 + 11.0, seed * 4.7 + 3.0, seed * 0.9 + 7.0))
    moves = []
    for v in bm.verts:
        if kind[v] != 0:
            moves.append(Vector())
            continue
        q = Vector((v.co.x, v.co.y, v.co.z)) * 0.55 + shift
        d = WEATHER * (0.7 * noise.noise(q) + 0.3 * noise.noise(q * 2.2))
        moves.append(v.normal * d * min(1.0, (v.co.z - SKIRT) / 1.5))
    for v, m in zip(bm.verts, moves):
        v.co += m


WEATHER = 0.11       # how far the weathering moves the stone (pixels, about)


def view_to_world(bm):
    """Each point TILT * z down the screen (the camera then sees it where the sprite draws it)."""
    for v in bm.verts:
        v.co.y -= TILT * max(v.co.z, 0.0)


# --- Painting ---------------------------------------------------------------------------------------------------------

def materials():
    def grey(index, roughness=0.62):
        return k.material("face_stone", palette=index, metallic=0.0, roughness=roughness)
    m = {i: grey(i) for i in (0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0a)}
    m["cap"] = k.material("face_inside", palette=0x05, metallic=0.0, roughness=0.7)
    return m


BANDS = [(-99.0, 0x02), (2.5, 0x03), (3.5, 0x04), (4.5, 0x05), (5.5, 0x06), (6.5, 0x07), (7.5, 0x08), (8.5, 0x09),
         (9.5, 0x0a)]


def shade_values(x, y, kinds, damaged):
    """Each point's grey value (BANDS) from how it lies, at arrays of its place in the camera's view (before the
    weathering) and its kind."""
    gx, gy = gradient(x, y, damaged)
    n = np.stack([-gx, -gy, 1.0 - TILT * gy], axis=1)          # the sheared surface's normal
    n /= np.linalg.norm(n, axis=1)[:, None]
    lit = n @ np.array(LIGHT) - LIGHT.z    # how much more (or less) of the sun than a face looking straight up
    feat = features(x, y)
    d = np.maximum(SHAPE.signed(x, y), 0.0)
    val = 7.4 + 1.8 * lit
    val += 0.9 * np.minimum(feat, 1.6)             # the features' tops lighter
    val += 1.45 * np.maximum(np.minimum(feat, 0.0), -2.8)   # the hollows darker
    val -= 4.2 * (1.0 - sstep(0.0, 3.0, d))        # the rim falling to the ground
    val -= 1.3 * sstep(16.0, 22.0, y)              # the crown, darker over the forehead
    boss = bump(x - AXIS, y, 0.0, 12.0, 7.1, 4.6, 2.8)
    val += 1.3 * boss                              # the forehead's broad lit boss
    # and its gleam: a crescent along the boss's left and lower edges, where the sprite lights it
    ou, oy = (x - AXIS) / 7.1, (y - 12.0) / 4.6
    rr = np.maximum(np.hypot(ou, oy), 1e-6)
    towards = sstep(0.3, 0.75, (-0.42 * ou - 0.91 * oy) / rr)
    val += 2.4 * towards * np.exp(-((rr - 0.98) / 0.15) ** 2)
    for side in (-1.0, 1.0):                       # the sockets dark all over, as the sprite draws them
        val -= 2.2 * bump(x - AXIS, y, side * 5.3, 2.4, 4.5, 2.4, 3.0)
    val -= 1.2 * bump(np.abs(x - AXIS), y, 10.5, -11.0, 3.0, 6.0, 2.0)   # the gaunt lower cheeks
    val = np.where(kinds == 1, 4.0, val)
    val = np.where(kinds == 2, 5.0, val)
    return val


def paint_values(bm, kind, rest, damaged):
    """Each vertex's grey value: shade_values() at its place in the camera's view before the weathering."""
    bm.verts.index_update()
    verts = list(bm.verts)
    x = np.array([rest[v][0] for v in verts])
    y = np.array([rest[v][1] for v in verts])
    kinds = np.array([kind[v] for v in verts])
    return [float(val) for val in shade_values(x, y, kinds, damaged)]


def paint_damage(obj, m):
    """The cracks near black (their walls shaded by the light) and the chips fresh, lighter stone (0x0a): the faces cut
    along the contours of crack_field() (at the weathered places, a tenth of a pixel off at most) and given their
    paint over the bands."""
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    x = np.array([v.co.x for v in bm.verts])
    y = np.array([v.co.y for v in bm.verts])
    depth, chips, _ = crack_field(x, y)
    tops = [v.co.z > SKIRT + 1e-4 for v in bm.verts]
    fields = {"crack": {v: (float(dd) - 0.25 if t else -1.0) for v, dd, t in zip(bm.verts, depth, tops)},
              "chip": {v: (float(cc) - 0.5 if t else -1.0) for v, cc, t in zip(bm.verts, chips, tops)}}
    for name, index in (("crack", 0x02), ("chip", 0x0a)):
        split_contour(bm, fields, name, 0.0)
        f = fields[name]
        slot = mk.slot_of(obj, m[index])
        for fc in bm.faces:
            if sum(f[v] for v in fc.verts) / len(fc.verts) > 1e-9:
                fc.material_index = slot
    bm.to_mesh(obj.data)
    bm.free()


# --- Build ----------------------------------------------------------------------------------------------------------

def build_whole(m, damaged):
    bm, kind = face_mesh(damaged)
    rest = {v: (v.co.x, v.co.y) for v in bm.verts}
    weather(bm, kind, 3)
    values = paint_values(bm, kind, rest, damaged)
    mesh = bpy.data.meshes.new("stone_face")
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new("stone_face", mesh)
    bpy.context.scene.collection.objects.link(obj)
    obj.data.materials.append(m[0x08])
    band_split(obj, values, [(lo, m[i]) for lo, i in BANDS])
    if damaged:
        paint_damage(obj, m)
    # band_split rebuilt the mesh (the old vertices and the cuts' new ones): move them all down the screen.
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    view_to_world(bm)
    bm.to_mesh(obj.data)
    bm.free()
    k.smooth(obj, 75)
    obj.data.update()
    return obj


def view_cut(source, box, cap_mat, z0=0.0):
    """polish_crag.cut (polish_coral_manta's: the caps given their material as soon as they are made, facing out of
    their cut, the faces' own winding kept, the uncut object's shading; the caps flat) along the planes the game's
    camera sees as the sprites' edges: x = x0 and x1 upright, y = y0 and y1 where the camera sees them at height z0
    (y + TILT (z - z0) = y0: planes leaning back up the screen), so that each piece holds what the camera sees in its
    sprite's box. box: (x0, x1, y0, y1), None for a side with no neighbour. None if nothing is inside."""
    x0, x1, y0, y1 = box
    corners = [source.matrix_world @ Vector(c) for c in source.bound_box]
    views = [c.y + TILT * (c.z - z0) for c in corners]
    if ((x0 is not None and max(c.x for c in corners) <= x0) or (x1 is not None and min(c.x for c in corners) >= x1)
            or (y0 is not None and max(views) <= y0) or (y1 is not None and min(views) >= y1)):
        return None
    obj = source.copy()
    obj.data = source.data.copy()
    bpy.context.scene.collection.objects.link(obj)
    cap_index = mk.slot_of(obj, cap_mat)
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    lean = Vector((0.0, 1.0, TILT)).normalized()
    planes = []
    if x0 is not None:
        planes.append((Vector((x0, 0, 0)), Vector((-1, 0, 0))))
    if x1 is not None:
        planes.append((Vector((x1, 0, 0)), Vector((1, 0, 0))))
    if y0 is not None:
        planes.append((Vector((0, y0, z0)), -lean))
    if y1 is not None:
        planes.append((Vector((0, y1, z0)), lean))
    for co, no in planes:
        if not bm.faces:
            break
        result = bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-6, plane_co=co,
                                        plane_no=no, clear_outer=True)
        edges = [e for e in result["geom_cut"] if isinstance(e, bmesh.types.BMEdge) and e.is_valid]
        open_edges = [e for e in edges if len(e.link_faces) == 1]
        if open_edges:
            filled = bmesh.ops.holes_fill(bm, edges=open_edges, sides=0)
            if filled["faces"]:
                for f in bmesh.ops.triangulate(bm, faces=filled["faces"])["faces"]:
                    f.normal_update()
                    if f.normal.dot(no) < 0:
                        f.normal_flip()
                    f.material_index = cap_index
                    f.smooth = False
    if not bm.faces:
        bm.free()
        bpy.data.objects.remove(obj)
        return None
    bm.normal_update()
    bm.faces.index_update()
    cap_ids = {f.index for f in bm.faces if f.material_index == cap_index and not f.smooth}
    bm.to_mesh(obj.data)
    bm.free()
    shading = mk.NormalSource(source)
    mesh = obj.data
    normals = []
    for poly in mesh.polygons:
        for li in poly.loop_indices:
            n = None
            if poly.index not in cap_ids:
                n = shading.normal(mesh.vertices[mesh.loops[li].vertex_index].co, poly.center)
            normals.append(tuple(n if n is not None else poly.normal))
    mesh.normals_split_custom_set(normals)
    return obj


def view_coverage(objects, w, h, centre=(0.0, 0.0)):
    """Which pixels of a w x h picture round centre the game's camera sees the objects at (rows of bools): a ray along
    the camera's line of sight through each pixel's middle, as the sprite would be drawn on the ground (z 0)."""
    depsgraph = bpy.context.evaluated_depsgraph_get()
    trees = [BVHTree.FromObject(o, depsgraph) for o in objects]
    d = Vector((0.0, TILT, -1.0)).normalized()
    out = []
    for r in range(h):
        row = []
        for c in range(w):
            x, yv = centre[0] + c + 0.5 - w / 2, centre[1] + h / 2 - (r + 0.5)
            z0 = 60.0
            origin = Vector((x, yv - z0 * TILT, z0))
            row.append(any(t.ray_cast(origin, d)[0] is not None for t in trees))
        out.append(row)
    return out


def sheet_mask(sheets, spec):
    sheet, sprite = spec.split()
    return k.sprite_mask(os.path.join(sheets, "enemy_%s.png" % sheet), int(sprite))


def whole_mask(sheets, look):
    mask = [[False] * 48 for _ in range(56)]
    for (names, sprites, box) in PIECES:
        part = sheet_mask(sheets, sprites[look])
        ox, oy = int(box[0] + 24), int(28 - box[3])
        for yy in range(28):
            for xx in range(24):
                if part[yy][xx]:
                    mask[oy + yy][ox + xx] = True
    return mask


def build():
    options = k.args()
    only = options["only"].split(",") if "only" in options else None
    looks = options.get("looks", "intact,damaged").split(",")
    sheets = options.get("check")
    out = mk.outdir(options)
    for look in (0, 1):
        if ("intact", "damaged")[look] not in looks:
            continue
        k.reset()
        m = materials()
        whole = build_whole(m, look == 1)
        triangulate([whole])
        bpy.context.scene.view_settings.view_transform = "Standard"
        label = ("intact", "damaged")[look]
        print("stone face %s whole: %d triangles, %d materials" % (label, mk.triangles([whole]),
                                                                      len(whole.data.materials)))
        if sheets:
            mk.compare("whole (%s) as the camera sees it" % label, view_coverage([whole], 48, 56),
                       whole_mask(sheets, look))
        if "whole" in options:
            mk.export([whole], options["whole"] + ("stone_face_damaged.glb" if look else "stone_face.glb"))
        for names, sprites, box in PIECES:
            name = names[look]
            if only and name not in only:
                continue
            open_box = tuple(None if abs(v) > 20.0 else v for v in box)
            pieces = [p for p in (view_cut(whole, open_box, m["cap"]),) if p is not None]
            centre = Vector(((box[0] + box[1]) / 2, (box[2] + box[3]) / 2, 0.0))
            mk.transform(pieces, Matrix.Translation(-centre))
            bpy.context.view_layer.update()
            whole.hide_render = True
            drop_unused(pieces)
            triangulate(pieces)
            pieces = [join(pieces, name)]
            pieces[0].data.name = name
            if sheets:
                mk.compare("%s (%s) as the camera sees it" % (name, sprites[look]), view_coverage(pieces, 24, 28),
                           sheet_mask(sheets, sprites[look]))
            mk.report(name, pieces, os.path.join(out, name + ".glb"))
            if "preview" in options:
                mk.preview(options["preview"] + name, pieces)
            for obj in pieces:
                data = obj.data
                bpy.data.objects.remove(obj)
                if data.users == 0:
                    bpy.data.meshes.remove(data)
            whole.hide_render = False


if __name__ == "__main__":
    build()
