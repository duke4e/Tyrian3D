"""CORAL's manta (sheet T, 2x2 sprites of 24 x 28 pixels; episode 5, ground enemies, armour 20 each), polished
(2026-10-21, round 24); it replaces wave3_v_sea.py's manta, wave3_at_manta.py's wing frames and wave3_ap_coral.py's
wreck of its head. CORAL sends it 17 times (events at t 1700-4470, type 10), always as one 72 x 56 picture of four
enemies moving together: 1206 (T 197, the left wing) at (x, y), 1207 (T 199, the back) at (x + 24, y - 10), 1208 (T 237,
the head) at (x + 24, y + 18), 1209 (T 201, the right wing) at (x + 48, y). No episode 6 level takes a CORAL wave.
No other enemy, launched ones included, shows any of its sprites; twins2.py (every sheet: mirrored, flipped, turned,
other ramps) finds no twin. The wings are near mirror images of each other about the picture's middle (x = 0; 25 of
their pixels' coverage differ, and the light), the body is its own mirror image about the middle of column 35 (x =
-0.5); 239 and 167 are 235 and 165 mirrored about column 35.

The animations (catalog.json, sprite_profile.py): the wings beat all the time (1206: 197 235 235 235 235 165 165 165
165 235 235 235 235 197 197 197; 1209 the same with 201 239 167): the frames draw each wing shorter as it rises, its
tip 4 and 8 pixels in (the right one 5 and 9), a row lower, its trailing edge a little lower; frame models
coral_manta_wing_235 / _165 / _239 / _167 (as before). The head animates while it fires (1208: 237 271 273 275 275
273 273 271 271 237, animate 2); 271-275 draw the whole head a pixel lower (their first row is 199's last one: the
front of the body pushed forward a pixel, the horns with it) and blow light between the horns: 271 a crackling band
from one horn's inner edge to the other's near their tips (rows 17-18, pale cyan and blue, ramps 8 and 9), 273 the
band thicker with a spark over it and two under it, 275 a cut crystal of light below the mouth (rows 18-23, widest at
row 19) with sparks round it: frame models coral_manta_head_271 / _273 / _275. The back has one frame. Shot, the head
becomes T 277 (enemy 0, dgr): drawn a pixel lower too, a burnt hole in the front of its body, scorched round it, its
horns broken off short (the right one splintered thinner): coral_manta_head_damaged, cut from the wreck.

As the sprites and their 4x upscales draw it (columns and rows of the picture): a blue-grey manta swimming down the
screen, its broad wings swept back to their tips (column 0 and 71 of row 14), arched down; their leading edges (the
lower outline, rows 14-37) rimmed in gold-brown (ramps 10 and 1, 0xa4-0xa5, 0x16-0x17), their trailing edges (the upper
outline, rows 13-17) in dark bronze (0xa2-0xa3); blue-grey (ramp 6, 0x63-0x69) with a blue streak along each wing (ramp
3, 0x35-0x37); a raised back, its rear a bronze hood (0xa2-0xa5) round two tall dark windows (columns 30-33 and 36-39 of
rows 11-21, 0x30 framed in 0x60, a bronze bar between them), a thin bronze tail up the screen from the hood (column
35 of rows 0-6); in front of the windows the body pale and ribbed (two light lines down it, lighter bands across), a
teal-blue glow at its front (0x82-0x89, 0x3b-0x3c) over the mouth, a dark line along the front edge (row 38); two dark
cephalic horns (0x51-0x52, 0x63-0x65) from the front corners down to row 47, their outer edges curving in to tips
that hook inward.

Built as such a creature: the body and wings one closed heightfield over the outline (traced along the sprites'
staircase, mirrored about x = -0.5, rounded by Chaikin; polish_coral_manta.split_contour cuts the grid along it): the
wings' middle surface arched from 2.9 at the body down to 0.9 at the tips, their thickness tapering, a little camber,
the edge rounded; a trunk rising over it along the body to a hump at the hood (8.5 high), two low keels and three
ribs across its front, the windows' panes set into it (a recess, its floor the glass); the underside a little lower
(the manta glides about a pixel over the floor), its flat parts merged into larger faces. The tail a tapering tube from
the hump to the piece's top edge; the horns lofted flattened lobes, rolled so that their inner faces turn up, hooking
in at their tips. Painted by zones cut along smooth contours (split_contour: the rims by their distance from the
outline's leading and trailing edges, the hood over a border across the back, the bar, the glass and its frame, the
mouth along the front edge, the throat's glow (ragged), the wings' streak (ragged)) and within each in bands of the
sprite's palette indices by how much a part faces up and the sun (the wings darker towards their tips, the front
lighter). The body's normals are the heightfield's own (by differences), carried into each pose; the parts are
band_split by their faces' light. The right wing is the left one mirrored but for its tip, drawn out a pixel (column
71).

The poses: the wings bend up about x = -12 and 12 (the wing pieces' inner edges, so that the static back and head
always meet them), the bend spread over 6 pixels and the rest of the wing turned rigidly (the frames shorten the whole
wing, not only its tip), by the angle that takes the tip in as far as the frame draws it (235 / 239: 43 and 47
degrees, 165 / 167: 58 and 61; the tips rise to 16 and 20), the raised tip a little down the screen. The blowing
frames and the wreck move the head
forward a pixel at the mouth and the horns, nothing at the cuts the back and the wings meet it along (the 2 pixels
behind the cut stretched to 3). The light between the horns: jagged tubes and beads of pale cyan (0x8e, emission 0.55)
and blue (0x9d, 0.45); 275's crystal a faceted brilliant lying along y, its facets in the two lights by how they face
the sun; the throat glows brighter while it blows (0x84 and 0x86 at 0.29 and 0.48, instead of 0x82-0x86 at
0.1-0.3). The wreck: a ragged hole
sunk 1.7 into the front of the body (black, 0x03 up its walls), scorched round it (0x64, 0x03, ash 0x08), three bits of
the throat's light left in it (0x84, 0.3), the horns' lofts ended short in jagged stumps.

Every pose is built whole and cut along the sprites' edges (x = -12, 12; y = 0) into its pieces (this script's cut():
polish_savara_boss.cut with the caps' material set as soon as they are made, so that a cap a second plane cuts keeps
it; the caps 0x65, shaded as if facing up, so that a neighbour's cut reads as the body's inside when a piece is shot
away), each piece moved so that its sprite's centre is its origin, every mesh triangulated (polish_k_pod.triangulate:
the same output with and without --check) and its parts joined into one mesh (polish_deli_boss.join).

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up from the floor (z 0; the pieces
stand from about 0.2 to 8.5, the raised wings to 20). The whole's origin is the middle of the picture's width on the
edge between the back and the head: column c is x = c + 0.5 - 36, row r is y = 27.5 - r. The pieces' centres: 197
(-24, 4), 199 (0, 14), 201 (24, 4), 237 (0, -14).

models.cfg: the model lines stay (coral_manta_wing_left / _back / _wing_right / _head, coral_manta_head_damaged,
coral_manta_wing_235 / _239 / _165 / _167, all origin); new: model coral_manta_head_271 / _273 / _275
enemies/coral_manta_head_<frame>.glb origin and frame t 271 / 273 / 275 coral_manta_head_<frame>; the sprite lines of
197, 199, 201, 237 and 277 get height=-4 (on the sea floor, as polish_coral_eel.py's eel). Replaces wave3_v_sea.py's
manta (MANTA, MANTA_AXIS, manta_whole(), manta_piece(), the v.pieced("coral_manta", ...) registration, its docstring
paragraph), wave3_at_manta.py (all of it), wave3_ap_coral.py's manta section (MANTA_DMG, manta_damaged(), the
v.pieced("coral_manta_damaged", ...) registration, its docstring paragraph) and the pixels only those read
(wave3_v_art.py's MANTA, MANTA_WING_MID, MANTA_WING_UP; wave3_ap_art.py's MANTA_DMG): remove them so that they don't
overwrite these models.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouettes of each
pose's whole and of each piece against enemy_T.png), --preview <prefix> (each pose's whole: top and 3/4 views; with
--pieces 1 each piece's too), --only <model,...>, --poses <rest,flap1,flap2,blow1,blow2,blow3,wreck> (default all),
--whole <prefix> (the uncut wholes as <prefix><pose>.glb), --stats 1 (the wholes' largest parts).
"""
import math
import os
import sys

import bmesh
import bpy
import mathutils.noise as noise
import numpy as np
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k  # noqa: E402
from polish_deli_boss import join, drop_unused  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402
from polish_orb_red import band_split  # noqa: E402

AXIS = -0.5            # the body's mirror axis: the middle of the picture's column 35
WIN_AXIS = -1.0        # the windows' (between the picture's columns 34 and 35)
GRID = 0.6             # the body's grid (pixels)
LIGHT = Vector((-0.6, 0.6, 1.0)).normalized()   # towards the game's sun
FLAT_LIGHT = LIGHT.z   # what a surface facing straight up gets of it

# The pieces: name, sprite, box (x0, x1, y0, y1) in the whole's coordinates (origin: the middle of the picture's
# width on the edge between the back and the head).
BOX = {"wing_left": (-36.0, -12.0, -10.0, 18.0), "back": (-12.0, 12.0, 0.0, 28.0),
       "wing_right": (12.0, 36.0, -10.0, 18.0), "head": (-12.0, 12.0, -28.0, 0.0)}
# The frames: what each builds (the pose, the pieces: name, sprite, box).
FRAMES = [
    ("rest", [("coral_manta_wing_left", 197, "wing_left"), ("coral_manta_back", 199, "back"),
              ("coral_manta_wing_right", 201, "wing_right"), ("coral_manta_head", 237, "head")]),
    ("flap1", [("coral_manta_wing_235", 235, "wing_left"), ("coral_manta_wing_239", 239, "wing_right")]),
    ("flap2", [("coral_manta_wing_165", 165, "wing_left"), ("coral_manta_wing_167", 167, "wing_right")]),
    ("blow1", [("coral_manta_head_271", 271, "head")]),
    ("blow2", [("coral_manta_head_273", 273, "head")]),
    ("blow3", [("coral_manta_head_275", 275, "head")]),
    ("wreck", [("coral_manta_head_damaged", 277, "head")]),
]
# The wings' tips (where the bend takes the outline's tip, left and right) for frames 235 / 239 and 165 / 167: the
# sprites draw the left one 4 and 8 pixels in, the right one 5 and 9 (its sprites a column shorter); the bent tip's
# underside reaches about a pixel further out.
FLAP_TIP = {"flap1": (30.6, 29.6), "flap2": (26.6, 25.6)}


def smoothstep(e0, e1, x):
    t = min(1.0, max(0.0, (x - e0) / (e1 - e0)))
    return t * t * (3 - 2 * t)


def sstep(e0, e1, x):
    """smoothstep for arrays."""
    t = np.clip((x - e0) / (e1 - e0), 0.0, 1.0)
    return t * t * (3 - 2 * t)


def curve(points, v):
    """Catmull-Rom through [(key, value)] (keys ascending), clamped at its ends."""
    if v <= points[0][0]:
        return points[0][1]
    if v >= points[-1][0]:
        return points[-1][1]
    for i in range(len(points) - 1):
        a, b = points[i][0], points[i + 1][0]
        if v <= b:
            t = (v - a) / (b - a)
            p0 = points[max(i - 1, 0)][1]
            p1, p2 = points[i][1], points[i + 1][1]
            p3 = points[min(i + 2, len(points) - 1)][1]
            return 0.5 * (2 * p1 + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t +
                          (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3)
    return points[-1][1]


def curve_np(points, v):
    return np.array([curve(points, float(a)) for a in np.atleast_1d(v)])


# --- The outline -----------------------------------------------------------------------------------------------------
# The left half, pixel edges of the 72 x 56 picture as (x, y) = (column - 36, 28 - row), from the axis at the hump's top
# round the left wing to the axis at the mouth; each point's tag names the edge the segment from it belongs to.
LEFT = [
    ((AXIS, 22.1), "hump"), ((-3.0, 21.95), "hump"), ((-4.1, 21.4), "hump"), ((-6.1, 20.6), "hump"),
    ((-7.1, 19.5), "hump"), ((-8.1, 18.5), "hump"), ((-9.1, 17.5), "hump"), ((-10.1, 16.5), "hump"),
    ((-11.1, 15.5), "hump"), ((-13.1, 14.5), "hump"), ((-14.1, 13.5), "hump"), ((-16.1, 12.5), "hump"),
    ((-19.1, 11.55), "trail"), ((-22.5, 11.05), "trail"), ((-25.2, 11.1), "trail"), ((-27.0, 12.0), "trail"),
    ((-28.6, 13.0), "trail"), ((-30.5, 14.3), "trail"), ((-33.0, 15.15), "trail"), ((-35.2, 14.95), "trail"),
    ((-36.45, 13.6), "lead"), ((-35.5, 12.2), "lead"), ((-34.2, 10.5), "lead"), ((-33.1, 9.5), "lead"),
    ((-31.1, 7.5), "lead"), ((-29.1, 5.5), "lead"), ((-28.15, 3.6), "lead"), ((-27.1, 2.5), "lead"),
    ((-25.15, 0.6), "lead"), ((-23.1, -0.5), "lead"), ((-21.1, -2.5), "lead"), ((-17.1, -4.5), "lead"),
    ((-13.1, -6.5), "lead"), ((-12.1, -7.5), "lead"), ((-11.15, -8.6), "front"), ((-11.1, -10.0), "front"),
    ((-10.4, -10.95), "front"), ((-8.0, -11.0), "front"), ((AXIS, -11.0), "front"),
]


def outline():
    """The whole outline (counter-clockwise from above): [(x, y)], [tag of the segment from each point]."""
    left = [p for p, _ in LEFT]
    tags = [t for _, t in LEFT]
    right = [(2 * AXIS - x, y) for x, y in reversed(left[1:-1])]
    right_tags = list(reversed(tags[1:-1]))
    pts = left + right
    seg_tags = tags[:-1] + [tags[-2]] + right_tags[1:] + [tags[0]]
    for _ in range(2):  # Chaikin
        out, out_tags = [], []
        n = len(pts)
        for i in range(n):
            p, q = pts[i], pts[(i + 1) % n]
            out += [(0.75 * p[0] + 0.25 * q[0], 0.75 * p[1] + 0.25 * q[1]),
                    (0.25 * p[0] + 0.75 * q[0], 0.25 * p[1] + 0.75 * q[1])]
            out_tags += [seg_tags[i], seg_tags[i]]
        pts, seg_tags = out, out_tags
    return pts, seg_tags


class Outline:
    """Distances to the outline (all of it, or the segments of some tags) and inside tests, for arrays of points."""

    def __init__(self):
        self.pts, self.tags = outline()
        p = np.array(self.pts)
        self.a = p
        self.b = np.roll(p, -1, axis=0)
        self.tag = np.array(self.tags)

    def _closest(self, x, y, sel):
        a, b = self.a[sel], self.b[sel]
        px, py = np.atleast_1d(x)[:, None], np.atleast_1d(y)[:, None]
        dx, dy = b[:, 0] - a[:, 0], b[:, 1] - a[:, 1]
        t = np.clip(((px - a[:, 0]) * dx + (py - a[:, 1]) * dy) / np.maximum(dx * dx + dy * dy, 1e-12), 0.0, 1.0)
        cx, cy = a[:, 0] + t * dx, a[:, 1] + t * dy
        d2 = (px - cx) ** 2 + (py - cy) ** 2
        i = np.argmin(d2, axis=1)
        rows = np.arange(len(i))
        return np.sqrt(d2[rows, i]), cx[rows, i], cy[rows, i]

    def distance(self, x, y, tags=None):
        sel = np.ones(len(self.a), bool) if tags is None else np.isin(self.tag, tags)
        x, y = np.atleast_1d(np.asarray(x, float)), np.atleast_1d(np.asarray(y, float))
        out = np.empty(len(x))
        for s in range(0, len(x), 4096):
            out[s:s + 4096] = self._closest(x[s:s + 4096], y[s:s + 4096], sel)[0]
        return out

    def nearest(self, x, y):
        _, cx, cy = self._closest(np.array([x]), np.array([y]), np.ones(len(self.a), bool))
        return float(cx[0]), float(cy[0])

    def inside(self, x, y):
        x, y = np.atleast_1d(np.asarray(x, float)), np.atleast_1d(np.asarray(y, float))
        out = np.empty(len(x), bool)
        a, b = self.a, self.b
        for s in range(0, len(x), 4096):
            px, py = x[s:s + 4096, None], y[s:s + 4096, None]
            cond = (a[:, 1] > py) != (b[:, 1] > py)
            den = np.where(b[:, 1] != a[:, 1], b[:, 1] - a[:, 1], 1e-12)
            xint = a[:, 0] + (py - a[:, 1]) * (b[:, 0] - a[:, 0]) / den
            out[s:s + 4096] = (cond & (px < xint)).sum(axis=1) % 2 == 1
        return out

    def signed(self, x, y):
        d = self.distance(x, y)
        return np.where(self.inside(x, y), d, -d)


# --- The body's heights ----------------------------------------------------------------------------------------------
ZR, ZT = 2.9, 0.9            # the wings' middle surface at the body and at the tips
TR, TT = 1.0, 0.28           # their half-thickness above it there
UNDER = 0.72                 # the half-thickness below, as a share of the one above
EDGE_R = 1.25                # the rounding of the outline's edge
CAMBER = 0.3                 # the middle of the wing above its edges
# the trunk: its half-width and its height over the wings along y
TRUNK_W = [(-11.0, 7.4), (-6.0, 8.2), (0.0, 8.8), (8.0, 8.8), (13.0, 8.0), (17.0, 6.6), (20.0, 5.4), (22.0, 4.8)]
TRUNK_H = [(-11.0, 1.0), (-8.0, 1.8), (-4.0, 2.6), (0.0, 3.0), (6.0, 3.2), (11.0, 3.8), (15.0, 4.3), (18.5, 3.7),
           (21.0, 2.4), (22.0, 2.0)]
BELLY = 0.5
UNDER_FLAT = 4.0             # (degrees) the underside's faces merged where they meet flatter than this
# the windows: set into the back, either side of WIN_AXIS (half-width from it, rows)
PANE_U = (1.0, 5.0)
PANE_Y = (6.0, 17.0)
PANE_R = 1.0
RECESS = 0.32
# the keels: two low ridges along the front of the body, and the ribs across it
KEEL_U, KEEL_H, KEEL_W = 3.0, 0.32, 0.75
KEEL_Y = (-9.0, 6.5)
RIBS = [5.0, 2.2, -0.6]
RIB_H, RIB_W = 0.13, 0.7


# The wreck (T 277, the head shot): a burnt hole in the front of the body (in the built frame: the sprite draws the
# head a pixel lower), ragged; scorched round it; the horns broken off short.
CRATER = ((-3.3, -6.1), (4.7, 2.9), 1.7, (0.28, 1.3))   # centre, radii, depth, ragged edge (how much, pixels across)
SCORCH = ((-1.8, -4.4), (7.6, 4.4), (0.3, 1.8))         # the scorched skin round it: centre, radii, ragged edge
HORN_BREAK = (-14.6, -16.6)                              # where the left and the right horn break off (y)
GLINTS = [((-3.4, -8.4), 0.32), ((1.7, -8.6), 0.3), ((-5.6, -7.3), 0.22)]   # bits of the throat's light in the hole
DAMAGED = {"on": False, "blowing": False}      # the pose being built: the wreck, a blowing frame


def ragged(x, y, scale, seed):
    return np.array([noise.noise(Vector((a / scale, b / scale, seed))) for a, b in zip(x, y)])


def crater_field(x, y):
    """Positive inside the hole (1 at its middle)."""
    (cx, cy), (rx, ry), _, (amount, scale) = CRATER
    return 1.0 - np.hypot((x - cx) / rx, (y - cy) / ry) + amount * ragged(x, y, scale, 8.8)


def pane_sd(x, y):
    """Signed distance (negative inside) to the nearer window pane's rounded rectangle."""
    u = np.abs(x - WIN_AXIS)
    cx, cy = (PANE_U[0] + PANE_U[1]) / 2, (PANE_Y[0] + PANE_Y[1]) / 2
    hx, hy = (PANE_U[1] - PANE_U[0]) / 2 - PANE_R, (PANE_Y[1] - PANE_Y[0]) / 2 - PANE_R
    qx, qy = np.abs(u - cx) - hx, np.abs(y - cy) - hy
    return np.hypot(np.maximum(qx, 0), np.maximum(qy, 0)) + np.minimum(np.maximum(qx, qy), 0) - PANE_R


def surface(shape, x, y, recess=True):
    """(top, bottom, d) of the body at arrays x, y; d: how far inside the outline."""
    x, y = np.atleast_1d(np.asarray(x, float)), np.atleast_1d(np.asarray(y, float))
    d = np.maximum(shape.signed(x, y), 0.0)
    u = np.abs(x - AXIS)
    s = np.clip((u - 8.0) / 27.0, 0.0, 1.0)
    zm = ZR - (ZR - ZT) * s ** 1.35 + CAMBER * sstep(0.0, 3.0, d)
    ht = TR - (TR - TT) * s ** 0.9
    dd = np.minimum(d, EDGE_R)
    edge = np.sqrt(np.maximum(0.0, dd * (2 * EDGE_R - dd))) / EDGE_R
    t = u / curve_np(TRUNK_W, y)
    trunk = curve_np(TRUNK_H, y) * np.exp(-1.6 * t * t) * (1.0 - sstep(1.2, 2.0, t)) * sstep(0.0, 2.6, d)
    keels = KEEL_H * np.exp(-((u - KEEL_U) / KEEL_W) ** 2) * sstep(KEEL_Y[0], KEEL_Y[0] + 2.0, y) * \
        sstep(KEEL_Y[1], KEEL_Y[1] - 2.0, y)
    ribs = sum(RIB_H * np.exp(-((y - r) / RIB_W) ** 2) for r in RIBS) * sstep(10.0, 6.0, u)
    top = zm + ht * edge + trunk + keels + ribs
    if recess:
        top = top - RECESS * sstep(0.45, -0.45, pane_sd(x, y))
    bottom = zm - UNDER * ht * edge - BELLY * trunk / 3.0
    if DAMAGED["on"]:
        depth = CRATER[2] * sstep(0.0, 0.45, crater_field(x, y))
        top = np.maximum(top - depth, bottom + 0.35)
    return top, bottom, d


def surface_normals(shape, x, y, which):
    """Analytic normals (finite differences) of the top (which 0) or bottom (1) at arrays x, y."""
    h = 0.04
    zx1 = surface(shape, x + h, y)[which]
    zx0 = surface(shape, x - h, y)[which]
    zy1 = surface(shape, x, y + h)[which]
    zy0 = surface(shape, x, y - h)[which]
    gx, gy = (zx1 - zx0) / (2 * h), (zy1 - zy0) / (2 * h)
    if which == 0:
        n = np.stack([-gx, -gy, np.ones_like(gx)], axis=1)
    else:
        n = np.stack([gx, gy, -np.ones_like(gx)], axis=1)
    return n / np.linalg.norm(n, axis=1)[:, None]


def rim_normals(shape, x, y):
    h = 0.04
    gx = (shape.signed(x + h, y) - shape.signed(x - h, y)) / (2 * h)
    gy = (shape.signed(x, y + h) - shape.signed(x, y - h)) / (2 * h)
    n = np.stack([-gx, -gy, np.zeros_like(gx)], axis=1)
    return n / np.maximum(np.linalg.norm(n, axis=1)[:, None], 1e-9)


# --- Poses -----------------------------------------------------------------------------------------------------------
HINGE = 12.0           # the wings bend about x = -12 and 12 (the wing pieces' inner edges)
HINGE_Z = 3.2          # the height of the bend's centre line there
RAMP = 6.0             # the bend is spread over this many pixels outboard of the hinge
TIP_DROP = 0.6        # a raised wing's tip comes down the screen this much (at 50 degrees; the frames draw it lower)
# The right wing is the left one's mirror image about AXIS, but for its tip, a pixel longer (rows 14-16 of the picture
# reach column 71): the tip drawn out.
TIP_WARP = (1.0, (28.0, 34.5), (10.0, 12.2))   # how far, from x to x, from y to y


def bend_map(s, h, angle):
    """A point s outboard of the hinge, h above the centre line, on a wing bent up by `angle` (radians; the bend
    spread over the first RAMP pixels, smoothly, the rest of the wing turned rigidly): (how far outboard, how high
    above the hinge's centre line)."""
    steps = max(1, int(math.ceil(s / 0.05)))
    ds = s / steps
    px = pz = 0.0
    for i in range(steps):
        a = angle * smoothstep(0.0, RAMP, (i + 0.5) * ds)
        px += math.cos(a) * ds
        pz += math.sin(a) * ds
    a = angle * smoothstep(0.0, RAMP, s)
    return px - math.sin(a) * h, pz + math.cos(a) * h


def flap_angle(tip_x):
    """The angle that brings the tip's outer edge (36.05 out, on the centre line) to |x| = tip_x."""
    lo, hi = 0.0, 1.5
    s = 36.05 - HINGE
    for _ in range(40):
        mid = (lo + hi) / 2
        if HINGE + bend_map(s, 0.0, mid)[0] > tip_x:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def lunge(x, y):
    """How far the head moves down the screen while it blows (1 pixel at the mouth and the horns, 0 at the cuts the
    back and the wings meet it along)."""
    if y >= 0.0:
        return 0.0
    c = smoothstep(0.0, -2.0, y)
    b = smoothstep(11.5, 9.0, abs(x - AXIS))
    e = smoothstep(-7.5, -9.5, y)
    return c * max(b, e)


def pose_point(p, pose):
    """Where a point of the built (symmetric) manta goes in a pose: the right wing's tip drawn out a pixel, then the
    wings bent up (flap) or the head moved a pixel forward (blow, wreck)."""
    x, y, z = p
    if x > TIP_WARP[1][0]:
        x += TIP_WARP[0] * smoothstep(*TIP_WARP[1], x) * smoothstep(*TIP_WARP[2], y)
    if pose in FLAP_TIP:
        if abs(x) > HINGE:
            side = 1.0 if x > 0 else -1.0
            angle = POSE_ANGLE[pose][side > 0]
            out, up = bend_map(abs(x) - HINGE, z - HINGE_Z, angle)
            y -= TIP_DROP * angle / math.radians(50.0) * smoothstep(0.0, 36.05 - HINGE, abs(x) - HINGE)
            x, z = side * (HINGE + out), HINGE_Z + up
    elif pose.startswith("blow") or pose == "wreck":
        y -= lunge(x, y)
    return Vector((x, y, z))


POSE_ANGLE = {}


def pose_normal(p, n, pose):
    """The normal n at p carried into the pose (the inverse transpose of the map's Jacobian, by differences)."""
    h = 0.02
    base = pose_point(p, pose)
    cols = []
    for axis in range(3):
        q = list(p)
        q[axis] += h
        cols.append((pose_point(q, pose) - base) / h)
    J = Matrix(((cols[0].x, cols[1].x, cols[2].x), (cols[0].y, cols[1].y, cols[2].y),
                (cols[0].z, cols[1].z, cols[2].z)))
    try:
        out = J.inverted().transposed() @ Vector(n)
    except ValueError:
        out = Vector(n)
    return out.normalized()


# --- Materials -------------------------------------------------------------------------------------------------------

def materials():
    pal = k.level_palette()
    m = {}
    skin = dict(metallic=0.25, roughness=0.38)
    for i in range(0x63, 0x6b):
        m[i] = k.material("manta_skin", palette=i, **skin)
    for i in (0xa2, 0xa3, 0xa4, 0xa5, 0x17):
        m[i] = k.material("manta_gold", palette=i, metallic=0.4, roughness=0.36)
    m["glass"] = k.material("manta_glass", palette=0x30, metallic=0.3, roughness=0.07)
    m["frame"] = k.material("manta_frame", palette=0x60, metallic=0.4, roughness=0.3)
    for i, glow in ((0x82, 0.1), (0x84, 0.18), (0x86, 0.3)):
        m[i] = k.material("manta_throat", palette=i, metallic=0.1, roughness=0.3, emission=pal[i],
                          emission_strength=glow)
        # (while it blows, brighter)
        m["charged", i] = k.material("manta_throat_lit", palette=i, metallic=0.1, roughness=0.3, emission=pal[i],
                                     emission_strength=glow * 1.6)
    for i, glow in ENERGY:
        m["energy", i] = k.material("manta_spark", palette=i, metallic=0.0, roughness=0.2, emission=pal[i],
                                    emission_strength=glow)
    m["mouth"] = k.material("manta_mouth", palette=0x30, metallic=0.0, roughness=0.6)
    for i in (0x35, 0x37):
        m[i] = k.material("manta_skin", palette=i, **skin)
    for i in (0x03, 0x08):
        m[i] = k.material("manta_burnt", palette=i, metallic=0.05, roughness=0.75)
    m["glint"] = k.material("manta_glint", palette=0x84, metallic=0.0, roughness=0.3, emission=pal[0x84],
                            emission_strength=0.3)
    for i in (0x51, 0x52):
        m[i] = k.material("manta_horn", palette=i, metallic=0.25, roughness=0.35)
    m["cap"] = m[0x65]
    return m


# --- The body mesh ---------------------------------------------------------------------------------------------------

def body_mesh(shape):
    """The body and wings as a bmesh: a grid over the outline, cut along it, its top and bottom at surface(); returns
    (bm, {vertex: rest position}, {vertex: rest normal}, top faces)."""
    nx = int(math.ceil(37.0 / GRID))
    xs = [AXIS + (i - nx) * GRID for i in range(2 * nx + 1)]
    ny = int(math.ceil(34.0 / GRID))
    ys = [-11.5 + j * GRID for j in range(ny + 1)]
    X, Y = np.meshgrid(np.array(xs), np.array(ys))
    sd = shape.signed(X.ravel(), Y.ravel()).reshape(X.shape)
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
    bm.verts.index_update()
    sdv = {}
    for v in bm.verts:
        dv = float(shape.signed([v.co.x], [v.co.y])[0])
        if abs(dv) < 0.3 * GRID:  # onto the outline: no slivers along it
            v.co.x, v.co.y = shape.nearest(v.co.x, v.co.y)
            dv = 0.0
        sdv[v] = dv
    split_contour(bm, {"sd": sdv}, "sd", 0.0)
    gone = [f for f in bm.faces if sum(sdv[v] for v in f.verts) / len(f.verts) < 0]
    bmesh.ops.delete(bm, geom=gone, context="FACES")
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
    top_faces = list(bm.faces)
    rim = [v for v in bm.verts if sdv[v] <= 1e-6]
    rim_set = set(rim)
    inner = [v for v in bm.verts if v not in rim_set]
    under = {v: bm.verts.new(v.co) for v in inner}
    for v in rim:
        under[v] = v
    bottom = []
    for f in top_faces:
        if all(v in rim_set for v in f.verts):
            continue
        bottom.append(bm.faces.new([under[v] for v in reversed(f.verts)]))
    rest, normal = {}, {}
    # heights and normals
    for group, which in ((inner, 0), ([under[v] for v in inner], 1)):
        if not group:
            continue
        x = np.array([v.co.x for v in group])
        y = np.array([v.co.y for v in group])
        z = surface(shape, x, y)[which]
        nn = surface_normals(shape, x, y, which)
        for v, zz, n in zip(group, z, nn):
            v.co.z = float(zz)
            rest[v] = v.co.copy()
            normal[v] = Vector(n)
    x = np.array([v.co.x for v in rim])
    y = np.array([v.co.y for v in rim])
    z = surface(shape, x, y)[0]
    nn = rim_normals(shape, x, y)
    for v, zz, n in zip(rim, z, nn):
        v.co.z = float(zz)
        rest[v] = v.co.copy()
        normal[v] = Vector(n)
    # the underside, seldom seen, in larger faces: its nearly flat parts dissolved (its edges along the rim kept)
    inner_edges = [e for e in {e for f in bottom for e in f.edges}
                   if all(fc in set(bottom) for fc in e.link_faces) and not all(v in rim_set for v in e.verts)]
    bmesh.ops.dissolve_limit(bm, angle_limit=math.radians(UNDER_FLAT), verts=[], edges=inner_edges,
                             delimit={"NORMAL"})
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
    return bm, rest, normal, {f for f in top_faces if f.is_valid}


def split_contour(bm, vals, name, t, faces=None):
    """Cuts the faces (all, or the given ones) along the contour where field `name` crosses t, the other fields
    interpolated at the new vertices; returns the given faces and the new ones."""
    target = set(bm.faces) if faces is None else {f for f in faces if f.is_valid}
    edges = set()
    for f in target:
        edges.update(f.edges)
    made = set()
    field = vals[name]
    order = sorted(edges, key=lambda e: tuple(sorted((tuple(e.verts[0].co), tuple(e.verts[1].co)))))
    for e in order:
        a, b = e.verts
        fa, fb = field[a], field[b]
        if (fa - t) * (fb - t) < 0:
            fac = (t - fa) / (fb - fa)
            _, v = bmesh.utils.edge_split(e, a, fac)
            for d in vals.values():
                va, vb = d[a], d[b]
                d[v] = va + (vb - va) * fac if not isinstance(va, Vector) else va.lerp(vb, fac)
            field[v] = t
            made.add(v)
    out = set()
    for f in sorted(target, key=lambda f: tuple(f.calc_center_median())):
        if not f.is_valid:
            continue
        out.add(f)
        ends = [v for v in f.verts if v in made or abs(field[v] - t) < 1e-9]
        if len(ends) == 2 and not any(ends[1] in e.verts for e in ends[0].link_edges):
            new, _ = bmesh.utils.face_split(f, ends[0], ends[1])
            out.add(new)
    return out


# --- Painting the body -----------------------------------------------------------------------------------------------
LEAD_W, TRAIL_W = 1.6, 1.25       # the rims' widths along the leading and the trailing edges
CAPE_BORDER = [(0.0, 10.6), (5.0, 10.5), (9.0, 10.9), (12.0, 11.6), (15.0, 12.6), (18.0, 14.0)]
DIVIDER = (0.95, 6.4, 17.4)        # the brown bar between the panes: half-width, from y, to y
THROAT = ((AXIS, -9.25), (5.0, 1.45))  # the glow in the throat over the mouth: centre, radii
THROAT_NOISE = (0.22, 1.6)             # its edge's irregularity: how much, how many pixels across
MOUTH = (0.75, 6.4)               # the dark mouth along the front edge: how far in, half-width
# shades: (lowest value, material key)
GREY_BANDS = [(-99, 0x63), (4.2, 0x64), (5.2, 0x65), (6.2, 0x66), (7.2, 0x67), (8.2, 0x68), (9.2, 0x69)]
THROAT_BANDS = [(-99, 0x82), (0.4, 0x84), (0.72, 0x86)]
THROAT_LIT_BANDS = [(-99, 0x84), (0.55, 0x86)]   # (while it blows: two, the sparks' two lights need the slots)
BLUE_BANDS = [(-99, 0x35), (5.4, 0x37)]
SOOT_BANDS = [(-99, "mouth"), (3.0, 0x03)]                       # the hole: black, dark grey up its walls
SCORCH_BANDS = [(-99, 0x64), (4.0, 0x03), (5.4, 0x08)]           # round it: dark skin, grey, ash
STREAKS = (5.4,)                  # the wings' blue streak: how far in from the leading edge
STREAK_W = 0.85                   # its half-width
STREAK_NOISE = (0.35, 2.4)
GOLD_BANDS = [(-99, 0xa4), (5.2, 0xa5), (6.6, 0x17)]
TRAIL_BANDS = [(-99, 0xa2), (3.6, 0xa3)]
CAPE_BANDS = [(-99, 0xa2), (3.0, 0xa3), (4.4, 0xa4), (5.8, 0xa5), (7.4, 0x17)]


def zone_fields(shape, rest_pts):
    """The zone fields at rest positions (each positive inside its zone)."""
    x = np.array([p.x for p in rest_pts])
    y = np.array([p.y for p in rest_pts])
    u = np.abs(x - AXIS)
    lead = LEAD_W - shape.distance(x, y, ["lead"])
    trail = TRAIL_W - shape.distance(x, y, ["trail"])
    cape = y - curve_np(CAPE_BORDER, u)
    div = np.minimum(DIVIDER[0] - np.abs(x - WIN_AXIS), np.minimum(y - DIVIDER[1], DIVIDER[2] - y))
    (cx, cy), (rx, ry) = THROAT
    wobble = np.array([noise.noise(Vector((a / THROAT_NOISE[1], b / THROAT_NOISE[1], 0.37))) for a, b in zip(x, y)])
    throat = 1.0 - np.hypot((x - cx) / rx, (y - cy) / ry) + THROAT_NOISE[0] * wobble
    dl = shape.distance(x, y, ["lead"])
    taper = sstep(11.5, 16.5, u) * sstep(33.0, 27.5, u)
    wobble = np.array([noise.noise(Vector((abs(a - AXIS) / STREAK_NOISE[1], b / STREAK_NOISE[1], 5.1)))
                       for a, b in zip(x, y)])
    streak = np.full(len(x), -9.0)
    for c in STREAKS:
        streak = np.maximum(streak, (STREAK_W + STREAK_NOISE[0] * wobble) * taper - np.abs(dl - c) - 0.05)
    pane = pane_sd(x, y)
    glass = -0.46 - pane
    frame = 0.34 - pane
    mouth = np.minimum(MOUTH[0] - shape.distance(x, y, ["front"]), MOUTH[1] - u)
    base = 8.1 - 3.0 * np.clip((u - 6.0) / 29.0, 0.0, 1.0) ** 0.8 + 0.7 * sstep(2.0, -6.0, y) * sstep(10.0, 4.0, u)
    if DAMAGED["on"]:
        soot = crater_field(x, y) + 0.12
        (sx, sy), (srx, sry), (amount, scale) = SCORCH
        scorch = 1.0 - np.hypot((x - sx) / srx, (y - sy) / sry) + amount * ragged(x, y, scale, 2.6)
        scorch = np.minimum(scorch, 2.0 * (-0.6 - y))     # (none at the cut the back meets it along)
        throat = np.minimum(throat, -1.0)
    else:
        soot = scorch = np.full(len(x), -1.0)
    return {"lead": lead, "trail": trail, "cape": cape, "div": div, "throat": throat, "glass": glass, "frame": frame,
            "mouth": mouth, "streak": streak, "soot": soot, "scorch": scorch, "base": base}


def zone_of(v):
    if v["soot"] > 0:
        return "soot"
    if v["scorch"] > 0 and v["lead"] <= 0:
        return "scorch"
    if v["lead"] > 0:
        return "gold"
    if v["trail"] > 0:
        return "trail"
    if v["glass"] > 0:
        return "glass"
    if v["frame"] > 0:
        return "frame"
    if v["cape"] > 0 or v["div"] > 0:
        return "cape"
    if v["mouth"] > 0:
        return "mouth"
    if v["throat"] > 0:
        return "throat"
    if v["streak"] > 0:
        return "blue"
    return "grey"


def paint_body(bm, rest, normal, tops, shape, m):
    """Zones (split along their borders) and shades (split along the bands) on the top; the underside dark."""
    verts = list(bm.verts)
    pts = [rest[v] for v in verts]
    f = zone_fields(shape, pts)
    vals = {name: {v: float(a) for v, a in zip(verts, arr)} for name, arr in f.items()}
    vals["n"] = {v: normal[v] for v in verts}
    light = {v: normal[v].normalized().dot(LIGHT) for v in verts}
    up = {v: normal[v].normalized().z for v in verts}
    vals["grey_v"] = {v: vals["base"][v] + 2.4 * (light[v] - FLAT_LIGHT) + 2.6 * (up[v] - 1.0) for v in verts}
    vals["gold_v"] = {v: 5.6 + 4.5 * (light[v] - FLAT_LIGHT) + 1.2 * (up[v] - 1.0) for v in verts}
    vals["trail_v"] = {v: 4.0 + 4.0 * (light[v] - FLAT_LIGHT) for v in verts}
    vals["cape_v"] = {v: 5.0 + 5.5 * (light[v] - FLAT_LIGHT) + 1.0 * (up[v] - 1.0) for v in verts}
    vals["soot_v"] = {v: 2.0 + 3.0 * (light[v] - FLAT_LIGHT) + 2.0 * min(1.0, vals["soot"][v] * -1.0 + 1.0)
                      for v in verts}
    vals["scorch_v"] = {v: 4.5 + 4.0 * (light[v] - FLAT_LIGHT) +
                        1.5 * noise.noise(rest[v] * 0.8 + Vector((1.0, 2.0, 3.0))) for v in verts}
    faces = {fc for fc in tops if fc.is_valid}
    for name in ("soot", "scorch", "lead", "trail", "glass", "frame", "cape", "div", "mouth", "throat", "streak"):
        faces = split_contour(bm, vals, name, 0.0, faces)

    def centre(fc):
        return {name: sum(vals[name][v] for v in fc.verts) / len(fc.verts) for name in f}
    zone = {fc: zone_of(centre(fc)) for fc in faces}
    plan = {"grey": ("grey_v", GREY_BANDS), "gold": ("gold_v", GOLD_BANDS), "trail": ("trail_v", TRAIL_BANDS),
            "cape": ("cape_v", CAPE_BANDS), "glass": (None, [(-99, "glass")]),
            "throat": ("throat", THROAT_LIT_BANDS if DAMAGED["blowing"] else THROAT_BANDS),
            "frame": (None, [(-99, "frame")]), "mouth": (None, [(-99, "mouth")]), "blue": ("grey_v", BLUE_BANDS),
            "soot": ("soot_v", SOOT_BANDS), "scorch": ("scorch_v", SCORCH_BANDS)}
    keys = []
    for z, (field, bands) in plan.items():
        zf = {fc for fc in zone if zone[fc] == z and fc.is_valid}
        if field:
            for lowest, _ in bands[1:]:
                zf = split_contour(bm, vals, field, lowest, zf)
        for fc in zf:
            zone[fc] = z
    slots = []
    for fc in bm.faces:
        z = zone.get(fc)
        if z is None:
            key = 0x63           # the underside
        else:
            field, bands = plan[z]
            key = bands[0][1]
            if field:
                value = sum(vals[field][v] for v in fc.verts) / len(fc.verts)
                for lowest, mat in bands:
                    if value >= lowest:
                        key = mat
        if key not in slots:
            slots.append(key)
        fc.material_index = slots.index(key)
    return slots, vals["n"]


def finish_body(bm, slots, normals, m, pose):
    """The painted bmesh as an object, its vertices in the pose, its normals the analytic ones carried along."""
    mesh = bpy.data.meshes.new("manta_body")
    verts = list(bm.verts)
    bm.verts.index_update()
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new("manta_body", mesh)
    bpy.context.scene.collection.objects.link(obj)
    for key in slots:
        mesh.materials.append(m[key])
    for p in mesh.polygons:
        p.use_smooth = True
    vn = [normals[v].normalized() for v in verts]
    mesh.normals_split_custom_set_from_vertices([tuple(n) for n in vn])
    return obj


def body(shape, m, pose):
    bm, rest, normal, tops = body_mesh(shape)
    # into the pose: positions and normals
    for v in bm.verts:
        p = rest[v]
        normal[v] = pose_normal(p, normal[v], pose)
        v.co = pose_point(p, pose)
    slots, normals = paint_body(bm, rest, normal, tops, shape, m)
    return finish_body(bm, slots, normals, m, pose)


# --- The tail and the horns ------------------------------------------------------------------------------------------
# the tail: (y, height of its axis, radius) from its root in the hump to its tip at the back piece's top edge
TAIL = [(17.0, None, 1.6), (19.5, None, 1.5), (21.4, 5.0, 1.15), (23.2, 4.65, 0.8), (25.4, 4.35, 0.6),
        (27.88, 4.05, 0.2)]
TAIL_BANDS = [(-99, 0xa3), (4.6, 0xa5), (6.2, 0x17)]
# the left horn: (x, y, height of its axis, half-width, half-height, roll (degrees, its inner edge up)) from its root
# in the head to its tip; the right one is its mirror image
HORN = [(-8.0, -7.4, 2.6, 2.6, 1.0, 0.0), (-8.05, -9.6, 2.45, 2.85, 0.98, 8.0), (-8.15, -11.6, 2.15, 2.9, 0.92, 15.0),
        (-8.05, -13.6, 1.88, 2.8, 0.86, 21.0), (-7.7, -15.4, 1.62, 2.55, 0.78, 26.0),
        (-7.15, -17.0, 1.38, 2.1, 0.66, 30.0), (-6.6, -18.35, 1.18, 1.45, 0.52, 32.0),
        (-6.25, -19.35, 1.04, 0.8, 0.36, 32.0),
        (-6.1, -19.9, 0.98, 0.28, 0.18, 32.0)]
HORN_BANDS = [(-99, 0x51), (3.4, 0x52), (4.6, 0x64), (5.8, 0x65), (7.0, 0x66)]

# --- The blowing frames' sparks (the frames' own pixel positions: they draw the head a pixel lower) -----------------
ENERGY = [(0x8e, 0.55), (0x9d, 0.45)]   # pale cyan and blue light: palette index, emission strength
# 271: a crackling arc between the horns' inner edges near their tips (rows 17-18, columns 7-15): its ends, its axis'
# height, how far its strands wander across it, their radius
ARC = ((-5.05, -18.0), (4.05, -18.0), 1.4, 0.55, 0.26)
# 273: the arc thicker and lower (rows 17-19), a spark over it and two under it (rows 14 and 21)
ARC2 = ((-5.0, -18.3), (4.0, -18.3), 1.45, 0.85, 0.3)
SPARKS2 = [((-1.5, -14.6), 0.42, 0x8e), ((-1.5, -21.5), 0.45, 0x8e), ((0.6, -21.4), 0.38, 0x9d)]
# 275: a cut crystal of light below the mouth (rows 18-23, widest at row 19, columns 8-14), sparks round it
GEM = ((-0.5, -18.35, 2.0), [(0.0, 2.3), (0.55, 3.25), (1.15, 3.35), (2.6, 1.9), (4.35, 0.25)], 0.58, 8)
SPARKS3 = [((-1.5, -16.5), 0.4, 0x8e), ((1.5, -16.4), 0.38, 0x8e), ((3.6, -17.4), 0.36, 0x8e),
           ((-4.5, -18.4), 0.4, 0x8e), ((-0.5, -14.6), 0.42, 0x8e), ((-4.6, -24.4), 0.4, 0x8e),
           ((1.6, -24.4), 0.36, 0x9d), ((-2.6, -23.4), 0.34, 0x9d)]


def tail(shape, m):
    pts, radii = [], []
    raw = []
    for y, z, r in TAIL:
        if z is None:
            z = float(surface(shape, [AXIS], [y])[0][0]) - 0.9 * r
        raw.append((y, z, r))
    for i in range(len(raw) - 1):
        for j in range(4 if i < len(raw) - 2 else 5):
            t = j / 4
            if i == len(raw) - 2 and j == 4:
                t = 1.0
            y = raw[i][0] + (raw[i + 1][0] - raw[i][0]) * t
            z = curve([(a, b) for a, b, _ in raw], y)
            r = curve([(a, c) for a, _, c in raw], y)
            pts.append((AXIS, y, z))
            radii.append(max(r, 0.08))
    obj = mk.tube("manta_tail", pts, 1.0, m[0xa3], segments=14, radii=radii)
    k.smooth(obj, 80)
    return obj


def loft_path(name, stations, mat, segments=16, power=2.2):
    """A tube through stations (x, y, z, half-width, half-height, roll degrees), its sections superellipses across the
    path (half-width level, half-height up, rolled about the path), its ends closed in points."""
    rings = []
    pts = [Vector(s[:3]) for s in stations]
    for i, st in enumerate(stations):
        t = (pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]).normalized()
        side = t.cross(Vector((0.0, 0.0, 1.0))).normalized()
        up = side.cross(t).normalized()
        roll = math.radians(st[5])
        side, up = side * math.cos(roll) + up * math.sin(roll), up * math.cos(roll) - side * math.sin(roll)
        ring = []
        for j in range(segments):
            a = 2 * math.pi * j / segments
            c, s_ = math.cos(a), math.sin(a)
            px = math.copysign(abs(c) ** (2 / power), c) * st[3]
            pz = math.copysign(abs(s_) ** (2 / power), s_) * st[4]
            ring.append(pts[i] + side * px + up * pz)
        rings.append(ring)
    first, last = pts[0] - (pts[1] - pts[0]).normalized() * 0.2, pts[-1] + (pts[-1] - pts[-2]).normalized() * 0.15
    obj = k.loft(name, rings, mat, start_point=first, end_point=last)
    return obj


def horns(m, broken=False):
    out = []
    for side in (1, -1):
        st = []
        stations = HORN if not broken else broken_horn(HORN_BREAK[0 if side > 0 else 1], side)
        for x, y, z, w, h, roll in stations:
            if side < 0:
                x, roll = 2 * AXIS - x, -roll
            st.append((x, y, z, w, h, roll * side))
        # (a path running down the screen has its "side" to the right of it: the left horn's inner edge is its left)
        obj = loft_path("manta_horn%d" % side, st, m[0x52], segments=18)
        k.smooth(obj, 80)
        out.append(obj)
    return out


def broken_horn(y_break, side):
    """The horn's stations down to where it breaks off, its end narrowed to a jagged stump (the right one, broken
    further down, splintered thinner)."""
    out = []
    for x, y, z, w, h, roll in HORN:
        if y > y_break:
            out.append((x, y, z, w, h, roll))
    x, y, z, w, h, roll = out[-1]
    thin = 1.0 if side > 0 else 0.62
    out[-1] = (x, y, z, w * thin, h, roll)
    out.append((x + 0.35 * side, y_break, z - 0.15, w * 0.55 * thin, h * 0.7, roll))
    out.append((x + 0.5 * side, y_break - 0.35, z - 0.2, w * 0.2 * thin, h * 0.35, roll))
    return out


def glints(m):
    return [mk.ball("manta_glint%d" % i, (x, y + 1.0, float(surface(SHAPE[0], [x], [y + 1.0])[0][0]) + 0.05),
                    (r, r, r * 0.8), m["glint"], 10, 6) for i, ((x, y), r) in enumerate(GLINTS)]


SHAPE = [None]


def paint_light(obj, m, bands, lift=0.0):
    """band_split by how a part faces the sun and up."""
    mesh = obj.data
    values = []
    vn = [Vector(v.normal) for v in mesh.vertices]
    for n in vn:
        values.append(5.0 + lift + 4.5 * (n.dot(LIGHT) - FLAT_LIGHT) + 1.5 * (n.z - 1.0))
    band_split(obj, values, [(lo, m[key]) for lo, key in bands])
    k.smooth(obj, 80)
    return obj


def strands(name, arc, m, count, seed):
    """Crackling light along an arc: jagged strands between its ends (zigzags, their corners wandering), bubbles of
    light strung along it, a bead at each end (the same each run)."""
    (ax, ay), (bx, by), z, wander, radius = arc
    out = []
    for k_ in range(count):
        pts = []
        n = 8
        for i in range(n + 1):
            t = i / n
            if 0 < i < n:
                t += 0.35 / n * noise.noise(Vector((i * 1.7, k_ * 2.3, seed)))
            env = math.sin(math.pi * t) ** 0.6
            zig = (1.0 if (i + k_) % 2 else -1.0) * (0.55 + 0.45 * noise.noise(Vector((i * 0.9 + seed, k_ * 1.1, 4.2))))
            dz = 0.3 * env * noise.noise(Vector((t * 3.1 + seed, 2.1 + k_, 0.5)))
            pts.append((ax + (bx - ax) * t, ay + (by - ay) * t + wander * env * zig, z + dz))
        key = ENERGY[k_ % len(ENERGY)][0]
        obj = mk.tube("%s%d" % (name, k_), pts, radius * (1.0 if k_ == 0 else 0.7), m["energy", key], segments=6)
        k.smooth(obj, 50)
        out.append(obj)
    for i in range(7):
        t = (i + 0.5) / 7
        x = ax + (bx - ax) * t
        y = ay + (by - ay) * t + wander * 1.1 * noise.noise(Vector((t * 5.3, seed, 7.7)))
        r = radius * (0.9 + 0.6 * abs(noise.noise(Vector((t * 4.1, seed, 1.9)))))
        key = ENERGY[i % 2][0]
        out.append(mk.ball("%s_bubble%d" % (name, i), (x, y, z + 0.2), (r, r, r * 0.9), m["energy", key], 10, 6))
    for i, (x, y) in enumerate(((ax, ay), (bx, by))):
        out.append(mk.ball("%s_end%d" % (name, i), (x, y, z), (radius * 1.4,) * 3, m["energy", 0x8e], 10, 6))
    return out


def sparks(name, specs, z, m):
    return [mk.ball("%s%d" % (name, i), (x, y, z + 0.25 * noise.noise(Vector((x, y, 1.7)))), (r, r, r * 0.9),
                    m["energy", key], 10, 6) for i, ((x, y), r, key) in enumerate(specs)]


def gem(m):
    """275's crystal of light: a brilliant-cut stone lying along the screen's y, its table towards the mouth and its
    point down the screen, faceted, its facets in the two lights by how they face the sun."""
    (cx, cy, cz), profile, squash, facets = GEM
    rings = []
    for d, r in profile:
        ring = []
        for j in range(facets):
            a = 2 * math.pi * (j + 0.5) / facets
            ring.append(Vector((cx + r * math.cos(a), cy - d, cz + r * math.sin(a) * squash)))
        rings.append(ring)
    obj = k.loft("manta_gem", rings, m["energy", 0x9d], start_point=(cx, cy + 0.05, cz),
                 end_point=(cx, cy - profile[-1][0] - 0.5, cz))
    mk.paint(obj, lambda c, n: m["energy", 0x8e] if n.dot(LIGHT) > 0.45 else m["energy", 0x9d])
    return obj


def energy(pose, m):
    if pose == "blow1":
        return strands("manta_arc", ARC, m, 2, 0.4)
    if pose == "blow2":
        return strands("manta_arc", ARC2, m, 3, 2.2) + sparks("manta_spark", SPARKS2, 1.5, m)
    if pose == "blow3":
        return [gem(m)] + sparks("manta_spark", SPARKS3, 1.6, m)
    return []


def place(obj, pose):
    for v in obj.data.vertices:
        v.co = pose_point(tuple(v.co), pose)
    obj.data.update()


def build_whole(pose):
    k.reset()
    m = materials()
    shape = Outline()
    SHAPE[0] = shape
    DAMAGED["on"] = pose == "wreck"
    DAMAGED["blowing"] = pose.startswith("blow")
    parts = [tail(shape, m)] + horns(m, broken=DAMAGED["on"]) + (glints(m) if DAMAGED["on"] else [])
    for obj in parts:
        place(obj, pose)
    paint_light(parts[0], m, TAIL_BANDS)
    for obj in parts[1:3]:
        paint_light(obj, m, HORN_BANDS, lift=1.6)
    if pose.startswith("blow"):   # the throat lit
        for i in (0x82, 0x84, 0x86):
            m[i] = m["charged", i]
    objs = [body(shape, m, pose)] + parts + energy(pose, m)
    return objs, m


# --- Cutting, checks and export ---------------------------------------------------------------------------------------

CAP_NORMAL = (0.0, 0.0, 1.0)   # the cuts shaded as the body's inside, lit like its top (seen when a piece is gone)


def cut(source, box_xy, cap_mat):
    """polish_savara_boss.cut (the part of an object inside a box (x0, x1, y0, y1), its cuts capped with cap_mat facing
    out of their cut, its normals the uncut object's, the faces' own winding kept), with the caps given their material
    as soon as they are made: a cap a later plane cuts in two keeps it (savara's gave the pieces the slot the hole fill
    had left them). None if nothing of the object is inside the box."""
    x0, x1, y0, y1 = box_xy
    corners = [source.matrix_world @ Vector(c) for c in source.bound_box]
    if (max(c.x for c in corners) <= x0 or min(c.x for c in corners) >= x1 or
            max(c.y for c in corners) <= y0 or min(c.y for c in corners) >= y1):
        return None
    obj = source.copy()
    obj.data = source.data.copy()
    bpy.context.scene.collection.objects.link(obj)
    cap_index = mk.slot_of(obj, cap_mat)
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    planes = (((x0, 0, 0), (-1, 0, 0)), ((x1, 0, 0), (1, 0, 0)), ((0, y0, 0), (0, -1, 0)), ((0, y1, 0), (0, 1, 0)))
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
                    if f.normal.dot(Vector(no)) < 0:
                        f.normal_flip()
                    f.material_index = cap_index
                    f.smooth = False
    if not bm.faces:
        bm.free()
        bpy.data.objects.remove(obj)
        return None
    on_cut = set()
    for f in bm.faces:
        if f.material_index == cap_index and not f.smooth:
            on_cut.add(f)
    bm.normal_update()
    bm.faces.index_update()
    cap_ids = {f.index for f in on_cut}
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
            normals.append(tuple(n if n is not None else CAP_NORMAL))
    mesh.normals_split_custom_set(normals)
    return obj
PLACES = {"wing_left": (0, 10), "back": (24, 0), "head": (24, 28), "wing_right": (48, 10)}


def whole_mask(sheet, sprites):
    """The pose's sprites placed as the levels place them: 72 x 56."""
    mask = [[False] * 72 for _ in range(56)]
    for part, sprite in sprites.items():
        c0, r0 = PLACES[part]
        for r, row in enumerate(k.sprite_mask(sheet, sprite)):
            for c, v in enumerate(row):
                if v:
                    mask[r0 + r][c0 + c] = True
    return mask


POSE_SPRITES = {"rest": {"wing_left": 197, "back": 199, "head": 237, "wing_right": 201},
                "flap1": {"wing_left": 235, "back": 199, "head": 237, "wing_right": 239},
                "flap2": {"wing_left": 165, "back": 199, "head": 237, "wing_right": 167},
                "blow1": {"wing_left": 197, "back": 199, "head": 271, "wing_right": 201},
                "blow2": {"wing_left": 197, "back": 199, "head": 273, "wing_right": 201},
                "blow3": {"wing_left": 197, "back": 199, "head": 275, "wing_right": 201},
                "wreck": {"wing_left": 197, "back": 199, "head": 277, "wing_right": 201}}


def export_pose(pose, pieces, options, sheet, out):
    only = options["only"].split(",") if "only" in options else None
    wanted = [p for p in pieces if not only or p[0] in only]
    if not wanted and "whole" not in options and "preview" not in options:
        return
    whole, m = build_whole(pose)
    triangulate(whole)
    low, high = mk.bounds(whole)
    print("== whole, %s: %d triangles, x %.2f..%.2f y %.2f..%.2f z %.2f..%.2f" % (
        pose, mk.triangles(whole), low.x, high.x, low.y, high.y, low.z, high.z))
    if "stats" in options:
        for obj in sorted(whole, key=lambda o: -mk.triangles([o]))[:8]:
            print("    %-22s %6d" % (obj.name, mk.triangles([obj])))
    if sheet:
        mk.compare("whole, %s" % pose, mk.coverage(whole, 72, 56), whole_mask(sheet, POSE_SPRITES[pose]))
    bpy.context.scene.view_settings.view_transform = "Standard"
    if "preview" in options:
        mk.preview(options["preview"] + "coral_manta_whole_" + pose, whole, size=(72, 56), scale=8, distance=2.0)
    if "whole" in options:
        mk.export(whole, options["whole"] + pose + ".glb")
    for name, sprite, part in wanted:
        box = BOX[part]
        parts = [p for p in (cut(src, box, m["cap"]) for src in whole) if p is not None]
        drop_unused(parts)
        mk.transform(parts, Matrix.Translation((-(box[0] + box[1]) / 2, -(box[2] + box[3]) / 2, 0)))
        bpy.context.view_layer.update()
        triangulate(parts)
        parts = [join(parts, name)]
        parts[0].data.name = name
        for src in whole:
            src.hide_render = True
        if sheet:
            mk.compare("%s (T %d)" % (name, sprite), mk.coverage(parts, 24, 28), k.sprite_mask(sheet, sprite))
        mk.report(name, parts, os.path.join(out, name + ".glb"))
        if "preview" in options and options.get("pieces") == "1":
            mk.preview(options["preview"] + name, parts)
        for obj in parts:
            bpy.data.objects.remove(obj)
        for src in whole:
            src.hide_render = False


def build():
    options = k.args()
    out = mk.outdir(options)
    sheet = None
    if "check" in options:
        sheets = options["check"]
        sheet = os.path.join(sheets, "enemy_T.png") if os.path.isdir(sheets) else sheets
    for pose, tips in FLAP_TIP.items():
        POSE_ANGLE[pose] = tuple(flap_angle(t) for t in tips)
    poses = options["poses"].split(",") if "poses" in options else [p for p, _ in FRAMES]
    for pose, pieces in FRAMES:
        if pose in poses:
            export_pose(pose, pieces, options, sheet, out)


if __name__ == "__main__":
    build()
