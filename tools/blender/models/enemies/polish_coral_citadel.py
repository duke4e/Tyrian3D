"""CORAL's citadel at the end of the level (sheet %, written x25 in models.cfg; 43 2x2 sprites of 24 x 28 pixels laid
out as the sheet lays them: % 1-17 above 39-55 above 77-93 above 115-131 above 155-167, 216 x 140 pixels; episode 5).
Polished (2026-10-22, round 35); it replaces wave3_al_citadel.py (all of it).

CORAL builds it from 43 custom enemies with armour 0 (events 49 and 52, shape bank 36 = sheet %; armour 0 makes them
decor the shots pass through: avail 2, never destroyed): at t5450 the rows 39-55, 77-93 and 115-131 at (54 + 24 i,
-112), (54 + 24 i, -84), (54 + 24 i, -56) and 155-167 at (78 + 24 i, -28), 28 ticks later the top row 1-17 at
(54 + 24 i, -112) (the ground has scrolled 28 pixels: it lies on top of 39-55), all link 9; its two blue eggs (polish_
coral_worm.py: ' 52 at t5462, ' 14 at t5490, x 92 and 210, each 28 pixels above the other) are put into its two bays.
At t5590 the citadel holds still at the top of the screen (global move eyc -1 against the scroll) while the sea floor
scrolls on under it, until the scroll stops at t6300; the level ends when both eggs are dead. No episode 6 level takes
it; no other enemy shows these sprites (the catalogue's other % sprites are FRUIT's, outside this picture).

As the sprites draw it (columns c and rows r of the 216 x 140 picture; it is its own mirror image about the line
between columns 108 and 109): the near half of a round fortress on the sea floor, its top cut straight where the
sprites stop. A great stone dome of blocks laid in stepped courses (grey 0x09 with dark joints 0x07 and a light edge
0x0a under and beside each joint; some blocks blue-grey 0x6a; the flanks two shades darker) over a dark wall (four rows
0x02-0x04 under its rim, five columns at its sides), a bright rounded lip along its foot (0x09-0x0c); in it two dark
bays (columns 35-63 and 154-182, rows 0-40: a chamfered rim, a black floor, two dark pods lying side by side with a
slot between them, rounded at their lower ends) where the eggs are put; at its top a red core glowing yellow-white in
its middle (columns 97-120, rows 8-33) in a dark ring, a thick blue steel pipe running from it up the screen out of the
picture (columns 101-116) in a dark sleeve. Round the dome's foot a purple trench (0x53-0x57), widest at the bottom
(rows 102-130), parted by five low walls a side into bays, in each bay a tall grey spike with a white tip (17 rows,
standing up the screen from a round foot) and a short one jutting from the foot of the dark wall; round the trench a
dark grey rampart (its crest a light line, its outer slope 0x04-0x05), cut by the picture's bottom edge in the middle.
The corners of the bottom row (FRUIT's sprites % 153 and 169) are not part of it.

Built for the game's camera (20 degrees off straight down, from the bottom of the screen): modelled in the picture's
plane (x, y as the sprites draw them, z up) and sheared along the camera's line of sight (y - z tan 20, normals with
it: polish_lava_grub.shear_to_camera's way), so that the camera sees every point where the sprites draw it; from above,
the outline stays the sprites'. The citadel is mirror symmetric about AXIS (x = 1).
- The body: one heightfield over the outline (a square grid of GRID pixels aligned with the sprites' edges, cut along
  smooth contours: polish_coral_manta.split_contour): the rampart (from the ground at the outline over a rounded crest
  down to the trench), the trench's floor with the low walls across it (ridges), the dark wall up to the dome's foot,
  the lip (a rounded bead), the dome rising from it to the core, the masonry's joints sunk into it (JOINTS: the sprites'
  joint lines, the blocks bevelled towards them), the bays sunk into it (a chamfered rim round a floor at Z_BAY, the
  eggs' base). The ring curves are superellipse arcs fitted to the sprites' borders (RINGS; their sides upright where
  the sprites run straight up), the zones and the shades within them cut along smooth contours, the normals the height
  function's own (by differences).
- The parts: the spikes (cones lofted from a round foot to a point, leaning up the screen as the sprites draw them: in
  the picture's plane their points lie SPIKE_RISE over their feet, which the shear leans back), the short spikes out of
  the wall's foot, the core (a glowing dome painted in the sprite's reds, yellow-white in its middle) in its dark ring,
  the pipe in its sleeve with a collar where it meets the core, the pods in the bays (under the eggs: they show when an
  egg is shot).
Painted with the sprites' palette indices in bands by the light each face gets (the game's sun from the top left) and
by zone: the blocks grey or blue-grey (BLUE: the sprites' blue-grey blocks), the joints dark, the lip bright, the
trench's bays each in its own purple (BAY_PURPLE), darker along the wall, the rampart dark with a lighter crest.

Cut into the 43 pieces in the picture's plane along the sprites' edges (the body's grid runs along them; the parts by
polish_coral_manta.cut's planes, unfilled: the pieces are never shot away, armour 0), sheared, each moved so that its
sprite's middle is its origin, triangulated (polish_k_pod.triangulate: the same output with and without --check) and
joined into one mesh (polish_deli_boss.join). Deterministic: no random numbers, no booleans.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up from the sea floor. The whole's
origin is the picture's column 108, row 70: column c is x = c + 0.5 - 108, row r is y = 69.5 - r. The pieces' origins:
sprite 1 + 2 i at (-96 + 24 i, 56), 39 + 2 i at (-96 + 24 i, 28), 77 + 2 i at (-96 + 24 i, 0), 115 + 2 i at (-96 + 24 i,
-28), 155 + 2 i at (-72 + 24 i, -56).

models.cfg: the 43 model lines stay (coral_citadel_<sprite> enemies/coral_citadel_<sprite>.glb origin); the 43 sprite
lines get height=-4 (on the sea floor: drawn at its origin a ground piece otherwise stands 4 pixels over it), the
core's piece (9) its glow moved onto the core (glow=26:0.3:120:1:7). The eggs (x27 14, 52) keep no height option: they
stand 4 pixels over the floor, on the bays' floors (Z_BAY). No frame lines (no animation).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the whole's silhouette as the
camera sees it and from straight above, and each piece's, against enemy_x25.png), --preview <prefix> (the whole: top
and 3/4 views), --only <name,...> (pieces to export), --whole <file.glb> (the uncut whole, sheared, for looking at),
--stats 1.
"""
import math
import os
import sys

import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
import polish_machine_kit as mk  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402
from polish_deli_boss import join, drop_unused  # noqa: E402
from polish_coral_manta import split_contour  # noqa: E402
from polish_orb_red import band_split  # noqa: E402

VIEW_TILT = 20.0
TAN_T = math.tan(math.radians(VIEW_TILT))
OX, OY = 108, 70                 # the whole's origin in the picture (column, row edge)
W, H = 216, 140
AXIS = 1.0                       # the mirror line (between columns 108 and 109)
GRID = 0.8                       # the body's grid (24 and 28 are multiples of it: the pieces' edges are grid lines)
LIGHT = Vector((-0.6, 0.6, 1.0)).normalized()   # towards the game's sun

# --- The rings (u = x - AXIS): superellipse arcs |u / A| ** P + ((CY - y) / B) ** P = 1 under CY, upright at |u| =
# SIDE where the arc would reach further out (fitted to the sprites' borders: rms 0.3-0.5 pixels).
RINGS = {
    "outer": (110.54, 109.30, 2.33, 39.30, 105.0),    # the rampart's foot (the outline)
    "crest": (104.62, 106.01, 2.56, 41.26, 102.5),    # the rampart's crest
    "trench_out": (103.75, 109.98, 2.60, 48.81, 100.0),   # the trench floor's outer edge
    "foot": (95.68, 40.95, 2.09, 13.10, 95.68),      # the dome's foot (the dark wall's top)
}
WALL_W = 4.3                     # the dark wall: the trench floor's inner edge lies this far outside the foot

# --- Heights (in the picture's plane) -------------------------------------------------------------------------------
Z_FLOOR = 1.0                    # the trench's floor
Z_CREST = 5.0                    # the rampart's crest
Z_FOOT = 8.0                     # the dark wall's top, the dome's foot
LIP_W, LIP_H = 4.0, 1.2          # the lip: a bead this wide and high along the foot
RISE, RISE_L = 17.0, 30.0        # the dome: rising RISE * (1 - exp(-d / RISE_L)) with the distance d from its foot
DIV_H, DIV_W = 2.6, 0.85         # the trench's low walls: height over the floor, half their width
JOINT_D, JOINT_W = 0.55, (0.3, 1.25)   # the joints: depth, the blocks' bevel (from the joint's line)
JOINT_PAINT = 0.5                # the joint's dark paint (half its width)

# --- The bays (the eggs' homes): middles u = -BAY_U and BAY_U, their round lower ends' middles at BAY_Y, floor radius
# BAY_R (the eggs' half width: their capsules stand on it), a chamfer up to the rim, a low raised rim round it.
BAY_U, BAY_Y, BAY_R = 59.0, 43.5, 12.0
Z_BAY = 4.0                      # the eggs stand 4 pixels over the floor (no height option): their base
CHAMFER, RIM_W, RIM_H = 2.5, 2.0, 0.6
PODS = (5.5, 4.6, 3.0, 40.0)     # the pods: offset from the bay's middle, half width, half height, their ends' middles

# --- The core and the pipe
CORE = (0.0, 49.0, 12.0, 13.0)   # u, y, radii (the sprite's ball, columns 97-120, rows 8-33)
CORE_H = 9.5                     # its dome over the dome's top
RING = (14.0, 2.0, 1.5)          # the dark ring: its middle's radius (over the core's), its half width, height
PIPE = (8.0, 6.0, 1.5, 58.5)     # half width, half height, its axis over the dome's top, where it starts (y)
SLEEVE = (11.0, 1.4)             # the dark sleeve under it: half width, height

# --- The joints between the dome's blocks (the sprites' joint lines, symmetrised: rows (r, c0, c1) and columns
# (c, r0, r1) of the left half and the middle; the right half is their mirror image).
JOINTS_H = [(1, 73, 85), (7, 14, 29), (10, 68, 77), (14, 26, 35), (14, 85, 98), (17, 64, 68), (30, 32, 37),
            (30, 65, 86), (35, 26, 32), (38, 65, 71), (38, 98, 119), (43, 48, 63), (43, 78, 98), (45, 16, 43),
            (46, 71, 78), (53, 14, 29), (54, 98, 119), (57, 63, 90), (59, 14, 22), (59, 43, 53), (62, 23, 34),
            (63, 97, 103), (65, 68, 78), (66, 53, 63), (67, 16, 23), (68, 34, 43), (72, 85, 100), (74, 27, 40),
            (76, 40, 56), (76, 61, 75), (80, 73, 90), (82, 97, 120), (84, 51, 56), (92, 85, 93)]
JOINTS_V = [(22, 67, 73), (23, 62, 67), (26, 14, 35), (27, 74, 78), (29, 7, 14), (29, 45, 53), (32, 30, 45),
            (34, 62, 68), (40, 74, 85), (43, 45, 68), (48, 40, 43), (51, 84, 88), (53, 59, 76), (56, 76, 84),
            (61, 76, 92), (63, 43, 66), (65, 30, 38), (68, 10, 17), (68, 65, 76), (71, 38, 46), (73, 0, 10),
            (73, 80, 94), (75, 76, 80), (77, 10, 30), (78, 43, 65), (85, 0, 14), (85, 72, 80), (86, 30, 43),
            (90, 57, 72), (90, 80, 92), (97, 63, 72), (97, 82, 97), (98, 38, 54), (100, 72, 82), (103, 54, 63)]
# The blue-grey blocks (rows r0-r1, columns c0-c1 of the left half; symmetrised, mirrored), grown into their joints.
BLUE = [(0, 9, 65, 71), (10, 16, 65, 67), (32, 37, 66, 84), (38, 42, 72, 84), (43, 45, 72, 77), (32, 44, 33, 46),
        (45, 58, 44, 61), (47, 54, 30, 41), (55, 58, 12, 41), (56, 64, 104, 113), (59, 61, 24, 41), (59, 64, 64, 76),
        (59, 65, 54, 61), (62, 67, 35, 41), (65, 66, 64, 66), (65, 71, 98, 119), (67, 75, 54, 66), (72, 81, 101, 116),
        (76, 85, 57, 59), (78, 83, 41, 54), (84, 86, 41, 49), (86, 88, 52, 59)]
BLUE_GROW = 0.6

# --- The trench: its low walls (inner end u, y; outer end u, y; the left half, mirrored), its bays' purples (from the
# middle out: the floor, the strip along the wall a shade darker), the spikes.
DIVIDERS = [((-17.0, -31.5), (-18.0, -58.5)), ((-32.5, -32.5), (-38.0, -56.5)), ((-47.5, -30.0), (-58.5, -51.5)),
            ((-63.5, -22.5), (-73.5, -39.0)), ((-83.5, -14.5), (-87.5, -24.0))]
BAY_PURPLE = [0x55, 0x56, 0x56, 0x56, 0x56, 0x55]
STRIP = 5.0                      # the darker strip along the wall
# The standing spikes: u, the foot's y, the point's y (as the sprites draw them), the foot's radius.
SPIKES = [(-11.5, -58.0, -40.0, 3.4), (-29.5, -56.0, -38.0, 3.4), (-45.5, -52.0, -34.0, 3.4),
          (-61.5, -44.0, -26.0, 3.4), (-77.5, -30.0, -20.0, 3.0), (-89.7, -12.0, -6.5, 2.4)]
SPIKE_RISE = 0.62                # their points' height over the floor: this times their length in the picture
# The short spikes out of the wall's foot, pointing down the screen: u, the foot's y, the point's y.
WALL_SPIKES = [(0.0, -32.0, -40.0), (-19.5, -31.0, -39.0), (-37.5, -28.0, -36.0), (-53.5, -25.0, -30.5),
               (-72.9, -12.0, -16.5), (-84.5, -4.0, -8.0)]

# --- Painting: shades (ramp 0 unless noted) by a light value (light()), per zone: (lowest value, palette index). At
# most 15 materials a piece: every grey shares one finish, the shades are few (the pieces holding the trench, the lip
# and blue blocks use nine greys, three purples and three blues).
DOME_BANDS = [(-99, 0x07), (4.4, 0x08), (5.6, 0x09), (6.8, 0x0a)]
FLANK_DARK = 1.8                 # the dome's flanks this much darker (the sprites' shading)
BLUE_BANDS = [(-99, 0x68), (5.0, 0x69), (6.3, 0x6a)]
LIP_BANDS = [(-99, 0x09), (4.8, 0x0a), (6.2, 0x0b)]
JOINT_INDEX = 0x05
WALL_BANDS = [(-99, 0x02), (5.4, 0x03)]
RAMPART_BANDS = [(-99, 0x03), (4.6, 0x05), (6.2, 0x07)]
INNER_FACE = 0x02
BAY_FLOOR = 0x02
DIVIDER_BANDS = [(-99, 0x03), (5.2, 0x05)]
CHAMFER_BANDS = [(-99, 0x05), (5.6, 0x07)]
RIM_BANDS = [(-99, 0x07), (6.2, 0x08)]
SPIKE_BANDS = [(-99, 0x07), (4.6, 0x09), (6.4, 0x0b)]
SPIKE_TIP = 0x0c
POD_BANDS = [(-99, 0x02), (4.5, 0x03), (5.6, 0x05), (6.8, 0x07)]
PIPE_BANDS = [(-99, 0x68), (4.8, 0x69), (5.8, 0x6a), (6.9, 0x6b)]
RING_BANDS = [(-99, 0x05), (6.0, 0x07)]
# The core's reds by the distance from its middle (0 rim, 1 middle): (lowest, index, emission)
CORE_BANDS = [(-99, 0x74, 0.22), (0.16, 0x77, 0.3), (0.42, 0x7a, 0.4), (0.68, 0x7c, 0.5), (0.88, 0x7e, 0.62)]
STONE = dict(metallic=0.12, roughness=0.62)
BLUE_FINISH = dict(metallic=0.12, roughness=0.6)

PIECE_ROWS = [(0, [1, 3, 5, 7, 9, 11, 13, 15, 17], 0), (28, [39, 41, 43, 45, 47, 49, 51, 53, 55], 0),
              (56, [77, 79, 81, 83, 85, 87, 89, 91, 93], 0), (84, [115, 117, 119, 121, 123, 125, 127, 129, 131], 0),
              (112, [155, 157, 159, 161, 163, 165, 167], 24)]
PIECES = [("coral_citadel_%d" % s, s, (c0 + 24 * i - OX, c0 + 24 * i + 24 - OX, OY - r0 - 28, OY - r0))
          for r0, sprites, c0 in PIECE_ROWS for i, s in enumerate(sprites)]


def sstep(e0, e1, x):
    t = np.clip((np.asarray(x, float) - e0) / (e1 - e0), 0.0, 1.0)
    return t * t * (3 - 2 * t)


# --- Fields ------------------------------------------------------------------------------------------------------------

class Ring:
    """A ring curve (RINGS) as a fine polyline from above the picture's top down round its bottom and up again (its
    corner where the arc meets its upright side rounded off over ROUND pixels); signed distances to it (positive
    inside: between its sides, over its bottom). The nearest of its coarse segments is found first, then the nearest
    fine one about it: the distance's slope turns smoothly inside the curve (no steps where coarse segments meet)."""
    FINE, PER = 0.15, 10           # the fine segments' length, fine segments to a coarse one
    ROUND = 6.0

    def __init__(self, spec):
        A, B, P, CY, side = spec
        self.A, self.B, self.P, self.CY, self.side = spec
        pts = []
        for i in range(40001):
            th = math.pi + math.pi * i / 40000
            c, s_ = math.cos(th), math.sin(th)
            u = A * math.copysign(abs(c) ** (2 / P), c)
            y = CY - B * abs(s_) ** (2 / P)
            if abs(u) <= side:
                pts.append((u, y))
        top = 80.0
        pts = [(-side, top), (-side, pts[0][1])] + pts + [(side, pts[-1][1]), (side, top)]
        a = np.array(pts)
        seg = np.hypot(np.diff(a[:, 0]), np.diff(a[:, 1]))
        dense_n = np.maximum(1, np.ceil(seg / 0.05).astype(int))
        dense = [a[0]]
        for p0, p1, n in zip(a[:-1], a[1:], dense_n):
            for t in range(1, n + 1):
                dense.append(p0 + (p1 - p0) * (t / n))
        dense = np.array(dense)
        # the corners rounded: a moving average along the curve (it leaves the smooth arc where it was)
        L = np.concatenate([[0.0], np.cumsum(np.hypot(np.diff(dense[:, 0]), np.diff(dense[:, 1])))])
        half = int(round(self.ROUND / 2 / 0.05))
        kern = np.ones(2 * half + 1) / (2 * half + 1)
        sm = np.stack([np.convolve(np.pad(dense[:, k_], half, mode="edge"), kern, mode="valid") for k_ in (0, 1)], 1)
        L = np.concatenate([[0.0], np.cumsum(np.hypot(np.diff(sm[:, 0]), np.diff(sm[:, 1])))])
        count = int(L[-1] / self.FINE / self.PER) * self.PER
        t = np.linspace(0.0, L[-1], count + 1)
        fine = np.stack([np.interp(t, L, sm[:, 0]), np.interp(t, L, sm[:, 1])], 1)
        self.fa, self.fb = fine[:-1], fine[1:]
        coarse = fine[::self.PER]
        self.ca, self.cb = coarse[:-1], coarse[1:]

    def half_width(self, y):
        y = np.asarray(y, float)
        q = np.clip((self.CY - y) / self.B, 0.0, 1.0)
        w = self.A * np.maximum(0.0, 1.0 - q ** self.P) ** (1.0 / self.P)
        w = np.minimum(w, self.side)
        return np.where(y <= self.CY - self.B, -1.0, w)

    def distance(self, u, y):
        _, idx = seg_distance(u, y, self.ca, self.cb, index=True)
        n = len(self.fa)
        win = idx[:, None] * self.PER + np.arange(-2 * self.PER, 3 * self.PER)[None, :]
        win = np.clip(win, 0, n - 1)
        a, b = self.fa[win], self.fb[win]
        dx, dy = b[..., 0] - a[..., 0], b[..., 1] - a[..., 1]
        l2 = np.maximum(dx * dx + dy * dy, 1e-12)
        t = np.clip(((u[:, None] - a[..., 0]) * dx + (y[:, None] - a[..., 1]) * dy) / l2, 0.0, 1.0)
        cx, cy = a[..., 0] + t * dx, a[..., 1] + t * dy
        return np.sqrt(((u[:, None] - cx) ** 2 + (y[:, None] - cy) ** 2).min(axis=1))

    def sd(self, u, y):
        u = np.asarray(u, float)
        y = np.asarray(y, float)
        d = self.distance(u, y)
        inside = np.abs(u) < self.half_width(y)
        return np.where(inside, d, -d)


def seg_distance(x, y, a, b, index=False):
    """Distances from points (arrays x, y) to the nearest of segments a[i]-b[i] (and that segment's index)."""
    dx, dy = b[:, 0] - a[:, 0], b[:, 1] - a[:, 1]
    l2 = np.maximum(dx * dx + dy * dy, 1e-12)
    out = np.empty(len(x))
    arg = np.empty(len(x), int)
    for s in range(0, len(x), 1024):
        px, py = x[s:s + 1024, None], y[s:s + 1024, None]
        t = np.clip(((px - a[:, 0]) * dx + (py - a[:, 1]) * dy) / l2, 0.0, 1.0)
        cx, cy = a[:, 0] + t * dx, a[:, 1] + t * dy
        d2 = (px - cx) ** 2 + (py - cy) ** 2
        arg[s:s + 1024] = d2.argmin(axis=1)
        out[s:s + 1024] = np.sqrt(d2.min(axis=1))
    return (out, arg) if index else out


def joint_segments():
    """The joints as segments in u, y (pixel centres to pixel centres), both halves."""
    segs = []
    for r, c0, c1 in JOINTS_H:
        y = OY - 0.5 - r
        for a0, a1 in ((c0, c1), (217 - c1, 217 - c0)):
            segs.append(((a0 + 0.5 - OX - AXIS, y), (a1 + 0.5 - OX - AXIS, y)))
    for c, r0, r1 in JOINTS_V:
        for cc in (c, 217 - c):
            u = cc + 0.5 - OX - AXIS
            segs.append(((u, OY - 0.5 - r0), (u, OY - 0.5 - r1)))
    segs = sorted(set(segs))
    return np.array([s[0] for s in segs]), np.array([s[1] for s in segs])


def blue_boxes():
    boxes = []
    for r0, r1, c0, c1 in BLUE:
        y0, y1 = OY - (r1 + 1) - BLUE_GROW, OY - r0 + BLUE_GROW
        for a0, a1 in ((c0, c1), (217 - c1, 217 - c0)):
            boxes.append((a0 - OX - AXIS - BLUE_GROW, a1 + 1 - OX - AXIS + BLUE_GROW, y0, y1))
    return np.array(boxes)


def divider_segments_lr():
    a, b = [], []
    for (u0, y0), (u1, y1) in DIVIDERS:
        # extended into the wall and the rampart's face (hidden there under their surfaces)
        d = np.array([u1 - u0, y1 - y0])
        d /= np.linalg.norm(d)
        for s in (1, -1):
            a.append((s * (u0 - 3.0 * d[0]), y0 - 3.0 * d[1]))
            b.append((s * (u1 + 3.0 * d[0]), y1 + 3.0 * d[1]))
    return np.array(a), np.array(b)


class Fields:
    """Every field of the body at points (u, y): the ring distances, the zones, the height."""

    def __init__(self):
        self.rings = {name: Ring(spec) for name, spec in RINGS.items()}
        self.ja, self.jb = joint_segments()
        self.boxes = blue_boxes()
        self.da, self.db = divider_segments_lr()
        # the dividers' lines (left half, outward) for telling the bays apart: angle-free, by side of each line
        self.div_lines = [(np.array(p0), np.array(p1)) for p0, p1 in DIVIDERS]

    def bay_sd(self, u, y):
        """Signed distance to the bays' floors (negative inside), both bays."""
        out = None
        for bu in (-BAY_U, BAY_U):
            dx = np.abs(u - bu)
            d = np.where(y >= BAY_Y, dx - BAY_R, np.hypot(dx, y - BAY_Y) - BAY_R)
            out = d if out is None else np.minimum(out, d)
        return out

    def core_sd(self, u, y):
        cu, cy, rx, ry = CORE
        q = np.hypot((u - cu) / rx, (y - cy) / ry)
        return (q - 1.0) * 0.5 * (rx + ry)

    def sleeve_sd(self, u, y):
        return np.maximum(np.abs(u) - SLEEVE[0], PIPE[3] - 2.0 - y)

    def blue_sd(self, u, y):
        b = self.boxes
        out = np.full(len(u), -99.0)
        for x0, x1, y0, y1 in b:
            d = np.minimum(np.minimum(u - x0, x1 - u), np.minimum(y - y0, y1 - y))
            out = np.maximum(out, d)
        return out

    def bay_index(self, u, y):
        """Which bay of the trench (0 the middle, 1.. outwards) a point lies in, by the side of the low walls."""
        au = np.abs(u)
        idx = np.zeros(len(u), int)
        for i, (p0, p1) in enumerate(self.div_lines):
            # the left half's wall: points left of it (further out) are in bay i + 1
            dx, dy = p1[0] - p0[0], p1[1] - p0[1]
            side = (-au - p0[0]) * dy - (y - p0[1]) * dx
            idx = np.where(side * -np.sign(dy) > 0, i + 1, idx)
        return idx

    def __call__(self, u, y):
        u = np.asarray(u, float)
        y = np.asarray(y, float)
        f = {}
        f["trench_out"] = self.rings["trench_out"].sd(u, y)
        f["foot"] = self.rings["foot"].sd(u, y)
        f["trench_in"] = f["foot"] + WALL_W
        ramp = f["trench_out"] < 0.5
        f["outer"] = np.full(len(u), 50.0)
        f["crest"] = np.full(len(u), 50.0)
        if ramp.any():
            f["outer"][ramp] = self.rings["outer"].sd(u[ramp], y[ramp])
            f["crest"][ramp] = self.rings["crest"].sd(u[ramp], y[ramp])
        f["bay"] = self.bay_sd(u, y)
        f["core"] = self.core_sd(u, y)
        f["sleeve"] = self.sleeve_sd(u, y)
        masonry = np.minimum.reduce([f["foot"] - LIP_W - 0.4, f["bay"] - (CHAMFER + RIM_W + 0.4), f["core"] - 3.0,
                                     f["sleeve"]])
        f["masonry"] = masonry
        dj = np.full(len(u), 50.0)
        near = masonry > -2.0
        if near.any():
            dj[near] = seg_distance(u[near], y[near], self.ja, self.jb)
        ddiv = np.full(len(u), 50.0)
        # the rampart: up from the outline to the crest, down its inner face to the floor
        d_o, d_c, d_to = f["outer"], f["crest"], f["trench_out"]
        t_out = np.clip(d_o / np.maximum(d_o - d_c, 1e-6), 0.0, 1.0)
        t_in = np.clip(d_c / np.maximum(d_c - d_to, 1e-6), 0.0, 1.0)
        z_ramp = np.where(d_c < 0, Z_CREST * sstep(0.0, 1.0, t_out) ** 0.85,
                          Z_FLOOR + (Z_CREST - Z_FLOOR) * (1.0 - sstep(0.0, 1.0, t_in)))
        # the floor, its low walls
        z_floor = np.full(len(u), Z_FLOOR)
        # the dark wall
        t_wall = np.clip(f["trench_in"] / WALL_W, 0.0, 1.0)
        z_wall = Z_FLOOR + (Z_FOOT - Z_FLOOR) * sstep(0.0, 1.0, t_wall)
        z_wall = np.maximum(z_wall, z_floor)
        # the dome: its rise, the lip, the joints
        d_f = np.maximum(f["foot"], 0.0)
        z_dome = Z_FOOT + RISE * (1.0 - np.exp(-d_f / RISE_L))
        lip = LIP_H * np.sin(np.pi * np.clip(d_f / LIP_W, 0.0, 1.0)) ** 2
        f["joint"] = np.minimum(JOINT_PAINT - dj, masonry)
        relief = -JOINT_D * (1.0 - sstep(JOINT_W[0], JOINT_W[1], dj)) * sstep(-0.3, 0.3, masonry)
        z_top = z_dome + lip + relief
        # the bays: the floor, the chamfer up to the dome, a low rim round it
        db = f["bay"]
        rim = RIM_H * np.sin(np.pi * np.clip((db - CHAMFER) / RIM_W, 0.0, 1.0)) ** 2
        z_top = np.where(db < CHAMFER + RIM_W, np.where(db <= 0.0, Z_BAY,
                         Z_BAY + (z_dome + rim - Z_BAY) * sstep(0.0, CHAMFER, db) ** 0.8), z_top)
        # assembled outward in
        z = np.where(f["trench_out"] < 0, z_ramp, np.where(f["trench_in"] < 0, z_floor,
                     np.where(f["foot"] < 0, z_wall, z_top)))
        f["z"] = z
        f["div"] = ddiv
        f["dj"] = dj
        return f


def normals_of(fields, u, y, h=0.03):
    """The height's normals at points (by differences), in the picture's plane."""
    zx = (fields(u + h, y)["z"] - fields(u - h, y)["z"]) / (2 * h)
    zy = (fields(u, y + h)["z"] - fields(u, y - h)["z"]) / (2 * h)
    n = np.stack([-zx, -zy, np.ones_like(zx)], axis=1)
    return n / np.linalg.norm(n, axis=1)[:, None]


def sheared(n):
    """A picture-plane normal as the shear turns it (the shear's inverse transpose)."""
    m = np.stack([n[:, 0], n[:, 1], n[:, 2] + TAN_T * n[:, 1]], axis=1)
    return m / np.linalg.norm(m, axis=1)[:, None]


def light(n, base=6.0, a=3.0, b=2.0):
    """A shade value from (sheared) normals: base facing straight up, more towards the sun, less away and down."""
    L = np.array(tuple(LIGHT))
    return base + a * (n @ L - LIGHT.z) + b * (n[:, 2] - 1.0)


# --- Materials ------------------------------------------------------------------------------------------------------

def materials():
    pal = k.level_palette()
    m = {}
    greys = set()
    for bands in (DOME_BANDS, LIP_BANDS, WALL_BANDS, RAMPART_BANDS, DIVIDER_BANDS, CHAMFER_BANDS, RIM_BANDS,
                  SPIKE_BANDS, POD_BANDS, RING_BANDS):
        greys |= {i for _, i in bands}
    greys |= {JOINT_INDEX, INNER_FACE, BAY_FLOOR, SPIKE_TIP}
    for i in sorted(greys):
        m[i] = m[("spike", i)] = k.material("citadel_stone", palette=i, **STONE)
    for i in sorted({i for _, i in BLUE_BANDS + PIPE_BANDS}):
        m[i] = m[("pipe", i)] = k.material("citadel_blue", palette=i, **BLUE_FINISH)
    for i in sorted(set(BAY_PURPLE + [p - 1 for p in BAY_PURPLE])):
        m[i] = k.material("citadel_silt", palette=i, metallic=0.05, roughness=0.8)
    for _, i, glow in CORE_BANDS:
        m[("core", i)] = k.material("citadel_core", palette=i, metallic=0.0, roughness=0.25, emission=pal[i],
                                    emission_strength=glow)
    return m


# --- The body ---------------------------------------------------------------------------------------------------------

def body(m, fields):
    """The heightfield over the outline (grid, contours, heights, normals, paint), as one object per piece: {name:
    object} (the grid runs along the pieces' edges)."""
    x0, x1, y0, y1 = -OX, W - OX, OY - H, OY
    ni, nj = int(round((x1 - x0) / GRID)), int(round((y1 - y0) / GRID))
    xs = x0 + GRID * np.arange(ni + 1)
    ys = y0 + GRID * np.arange(nj + 1)
    X, Y = np.meshgrid(xs, ys)
    out = fields.rings["outer"].sd(X.ravel() - AXIS, Y.ravel()).reshape(X.shape)
    bm = bmesh.new()
    verts = {}
    for j in range(nj + 1):
        for i in range(ni + 1):
            if out[j, i] > -2 * GRID:
                verts[i, j] = bm.verts.new((float(xs[i]), float(ys[j]), 0.0))
    for j in range(nj):
        for i in range(ni):
            q = [(i, j), (i + 1, j), (i + 1, j + 1), (i, j + 1)]
            if not all(c in verts for c in q) or max(out[c[1], c[0]] for c in q) <= 0:
                continue
            a, b, c, d = (verts[p] for p in q)
            if (i + j) % 2 == 0:
                bm.faces.new((a, b, c))
                bm.faces.new((a, c, d))
            else:
                bm.faces.new((a, b, d))
                bm.faces.new((b, c, d))
    verts = list(bm.verts)
    u = np.array([v.co.x for v in verts]) - AXIS
    y = np.array([v.co.y for v in verts])
    f = fields(u, y)
    f["blue"] = fields.blue_sd(u, y)
    f["lipzone"] = LIP_W - f["foot"]
    f["chamferzone"] = CHAMFER - f["bay"]
    f["rimzone"] = CHAMFER + RIM_W - f["bay"]
    f["strip"] = STRIP + f["trench_in"]
    names = ("outer", "crest", "trench_out", "trench_in", "foot", "bay", "core", "sleeve", "masonry", "joint", "blue",
             "lipzone", "chamferzone", "rimzone", "strip")
    vals = {name: {v: float(a) for v, a in zip(verts, f[name])} for name in names}
    # the outline: the grid cut along it, what lies outside dropped
    split_contour(bm, vals, "outer", 0.0)
    gone = [fc for fc in bm.faces if sum(vals["outer"][v] for v in fc.verts) / len(fc.verts) < 0]
    bmesh.ops.delete(bm, geom=gone, context="FACES")
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context="VERTS")
    # the zones' borders: geometry (the heights change their course along them) and paint
    for name in ("trench_out", "crest", "trench_in", "foot", "lipzone", "bay", "chamferzone", "rimzone"):
        split_contour(bm, vals, name, 0.0)
    # the joints and the blue blocks inside the masonry, the low walls' feet, the darker strip along the wall
    split_contour(bm, vals, "joint", 0.0, {fc for fc in bm.faces if max(vals["masonry"][v] for v in fc.verts) > -0.5})
    split_contour(bm, vals, "blue", 0.0, {fc for fc in bm.faces if max(vals["masonry"][v] for v in fc.verts) > -0.5})
    split_contour(bm, vals, "strip", 0.0, {fc for fc in bm.faces if fc.is_valid and
                                           min(vals["trench_out"][v] for v in fc.verts) > -0.01 and
                                           max(vals["trench_in"][v] for v in fc.verts) < 0.01})

    def avg(fc, name):
        return sum(vals[name][v] for v in fc.verts) / len(fc.verts)

    def zone(fc):
        if avg(fc, "trench_out") < 0:
            return "inner_face" if avg(fc, "crest") > 0 else "rampart"
        if avg(fc, "trench_in") < 0:
            return "floor"
        if avg(fc, "foot") < 0:
            return "wall"
        if avg(fc, "bay") < 0:
            return "bay_floor"
        if avg(fc, "bay") < CHAMFER:
            return "chamfer"
        if avg(fc, "bay") < CHAMFER + RIM_W:
            return "rim"
        if avg(fc, "foot") < LIP_W:
            return "lip"
        if avg(fc, "joint") > 0:
            return "joint"
        if avg(fc, "blue") > 0 and avg(fc, "masonry") > -0.5:
            return "blue"
        return "dome"

    # the light at every vertex so far, the bands within the zones cut along it
    verts = list(bm.verts)
    u = np.array([v.co.x for v in verts]) - AXIS
    y = np.array([v.co.y for v in verts])
    lv = light(sheared(normals_of(fields, u, y)))
    vals["light"] = {v: float(a) for v, a in zip(verts, lv)}
    vals["shade"] = {v: float(a) for v, a in zip(verts, lv - FLANK_DARK * np.clip(np.abs(u) / 95.0, 0.0, 1.0) ** 3)}
    zones = {fc: zone(fc) for fc in bm.faces}
    band_sets = {"rampart": RAMPART_BANDS, "wall": WALL_BANDS, "chamfer": CHAMFER_BANDS, "rim": RIM_BANDS,
                 "lip": LIP_BANDS, "blue": BLUE_BANDS, "dome": DOME_BANDS}
    by = {"blue": "shade", "dome": "shade", "lip": "shade"}
    for zname, bands in band_sets.items():
        zf = {fc for fc in zones if zones[fc] == zname and fc.is_valid}
        for lowest, _ in bands[1:]:
            zf = split_contour(bm, vals, by.get(zname, "light"), lowest, zf)
        for fc in zf:
            zones[fc] = zname
    bays = fields.bay_index(u, y)
    purple = {v: BAY_PURPLE[min(int(b_), len(BAY_PURPLE) - 1)] for v, b_ in zip(verts, bays)}
    # final heights and normals of every vertex (the cuts made new ones)
    verts = list(bm.verts)
    u = np.array([v.co.x for v in verts]) - AXIS
    y = np.array([v.co.y for v in verts])
    z = fields(u, y)["z"]
    nn = normals_of(fields, u, y)
    for v, zz in zip(verts, z):
        v.co.z = float(zz)
    normal = {v: tuple(n) for v, n in zip(verts, nn)}
    later = fields.bay_index(u, y)
    for v, b_ in zip(verts, later):
        if v not in purple:
            purple[v] = BAY_PURPLE[min(int(b_), len(BAY_PURPLE) - 1)]
    keys = {}
    for fc in bm.faces:
        zn = zones.get(fc, "dome")
        if zn in band_sets:
            value = avg(fc, by.get(zn, "light"))
            key = band_sets[zn][0][1]
            for lowest, i in band_sets[zn]:
                if value >= lowest:
                    key = i
        elif zn == "floor":
            p = min(purple[v] for v in fc.verts)
            key = p - 1 if avg(fc, "strip") > 0 else p
        elif zn == "joint":
            key = JOINT_INDEX
        elif zn == "inner_face":
            key = INNER_FACE
        else:
            key = BAY_FLOOR
        keys[fc] = key
    # one object per piece
    pieces = {}
    by_piece = {}
    for fc in bm.faces:
        c = fc.calc_center_median()
        for name, _, (bx0, bx1, by0, by1) in PIECES:
            if bx0 <= c.x <= bx1 and by0 <= c.y <= by1:
                by_piece.setdefault(name, []).append(fc)
                break
    for name, _, _ in PIECES:
        faces = by_piece.get(name)
        if not faces:
            continue
        nb = bmesh.new()
        index, slots, order = {}, [], []
        for fc in faces:
            for v in fc.verts:
                if v not in index:
                    index[v] = nb.verts.new(v.co)
                    order.append(v)
            nf = nb.faces.new([index[v] for v in fc.verts])
            if keys[fc] not in slots:
                slots.append(keys[fc])
            nf.material_index = slots.index(keys[fc])
        mesh = bpy.data.meshes.new(name + "_body")
        nb.to_mesh(mesh)
        nb.free()
        obj = bpy.data.objects.new(name + "_body", mesh)
        bpy.context.scene.collection.objects.link(obj)
        for key in slots:
            mesh.materials.append(m[key])
        for p in mesh.polygons:
            p.use_smooth = True
        mesh.normals_split_custom_set_from_vertices([normal[v] for v in order])
        pieces[name] = obj
    bm.free()
    return pieces


# --- The parts ----------------------------------------------------------------------------------------------------------

def loft_axis(name, base, tip, profile, mat, segments=14):
    """A solid turned about the axis from base to tip: profile [(t 0..1 along it, radius)], closed at both ends."""
    base, tip = Vector(base), Vector(tip)
    axis = tip - base
    length = axis.length
    d = axis.normalized()
    ref = Vector((1.0, 0.0, 0.0))
    e1 = (ref - d * ref.dot(d)).normalized()
    e2 = d.cross(e1)
    rings = []
    for t, r in profile:
        c = base + axis * t
        rings.append([c + (e1 * math.cos(2 * math.pi * j / segments) + e2 * math.sin(2 * math.pi * j / segments)) * r
                      for j in range(segments)])
    obj = k.loft(name, rings, mat, start_point=tuple(base - d * 0.0), end_point=tuple(tip))
    return obj


def paint_by_light(obj, bands, m, key=None, lift=0.0):
    """band_split by the light the faces get once sheared (vertex normals from the mesh's smooth shading)."""
    mesh = obj.data
    nn = np.array([tuple(v.normal) for v in mesh.vertices])
    lv = light(sheared(nn)) + lift
    band_split(obj, lv, [(lo, m[(key, i)] if key else m[i]) for lo, i in bands])
    k.smooth(obj, 70)
    return obj


def spikes(m, fields):
    out = []
    for side in (1, -1):
        for n, (u, yb, yt, r) in enumerate(SPIKES):
            uu = side * u + AXIS
            length = yt - yb
            base = (uu, yb, Z_FLOOR - 0.4)
            tip = (uu, yt, Z_FLOOR + SPIKE_RISE * length)
            prof = [(0.0, r * 1.05), (0.06, r * 1.12), (0.16, r * 1.0), (0.28, r * 0.72), (0.45, r * 0.5),
                    (0.7, r * 0.3), (0.9, r * 0.13), (1.0, 0.02)]
            obj = loft_axis("spike%d_%d" % (side, n), base, tip, prof, m[("spike", 0x08)], 14)
            k.smooth(obj, 80)
            mesh = obj.data
            nn = np.array([tuple(v.normal) for v in mesh.vertices])
            lv = light(sheared(nn))
            tz = np.array([v.co.z for v in mesh.vertices])
            hi = Z_FLOOR + SPIKE_RISE * length
            lv = np.where(tz > Z_FLOOR + 0.82 * (hi - Z_FLOOR), 99.0, lv)
            band_split(obj, lv, [(lo, m[("spike", i)]) for lo, i in SPIKE_BANDS] + [(98.0, m[("spike", SPIKE_TIP)])])
            k.smooth(obj, 80)
            out.append(obj)
        for n, (u, yb, yt) in enumerate(WALL_SPIKES):
            if side == -1 and u == 0.0:
                continue
            uu = side * u + AXIS
            base = (uu, yb + 0.8, Z_FLOOR + 1.9)
            tip = (uu, yt, Z_FLOOR + 1.3)
            prof = [(0.0, 1.6), (0.2, 1.35), (0.55, 0.75), (0.85, 0.25), (1.0, 0.02)]
            obj = loft_axis("wspike%d_%d" % (side, n), base, tip, prof, m[("spike", 0x08)], 10)
            k.smooth(obj, 80)
            mesh = obj.data
            nn = np.array([tuple(v.normal) for v in mesh.vertices])
            lv = light(sheared(nn))
            ty = np.array([v.co.y for v in mesh.vertices])
            lv = np.where(ty < yt + 0.2 * (yb - yt), 99.0, lv)
            band_split(obj, lv, [(lo, m[("spike", i)]) for lo, i in SPIKE_BANDS] + [(98.0, m[("spike", SPIKE_TIP)])])
            k.smooth(obj, 80)
            out.append(obj)
    return out


def dividers(m):
    """The low walls across the trench: bars of a rounded section from inside the dark wall to inside the rampart's
    face (their ends hidden under those), standing on the floor."""
    out = []
    a, b = divider_segments_lr()
    for n, (p0, p1) in enumerate(zip(a, b)):
        p0, p1 = Vector((p0[0] + AXIS, p0[1], 0.0)), Vector((p1[0] + AXIS, p1[1], 0.0))
        d = (p1 - p0).normalized()
        side = Vector((-d.y, d.x, 0.0))
        rings = []
        for t in np.linspace(0.0, 1.0, 9):
            c = p0.lerp(p1, float(t))
            ring = []
            for j in range(12):
                a_ = 2 * math.pi * j / 12
                cs, sn = math.cos(a_), math.sin(a_)
                w = DIV_W * math.copysign(abs(cs) ** 0.5, cs)
                hz = (Z_FLOOR + DIV_H * 0.55) + (DIV_H * 0.45 + 0.6) * math.copysign(abs(sn) ** 0.7, sn)
                ring.append(c + side * w + Vector((0.0, 0.0, hz)))
            rings.append(ring)
        obj = k.loft("divider%d" % n, rings, m[0x05], start_point=tuple(p0 + Vector((0, 0, Z_FLOOR + DIV_H * 0.4))),
                     end_point=tuple(p1 + Vector((0, 0, Z_FLOOR + DIV_H * 0.4))))
        k.smooth(obj, 50)
        paint_by_light(obj, DIVIDER_BANDS, m)
        out.append(obj)
    return out


def dome_top(fields, u, y):
    return float(fields(np.array([u]), np.array([y]))["z"][0])


def core(m, fields):
    """The glowing core (a dome over the sprite's ball) in its dark ring."""
    cu, cy, rx, ry = CORE
    x0 = cu + AXIS
    zb = dome_top(fields, cu, cy) - 0.6
    rings = []
    steps = 14
    for i in range(steps + 1):
        a = (math.pi / 2) * i / steps
        rr, zz = math.cos(a), math.sin(a)
        rings.append([Vector((x0 + rx * rr * math.cos(2 * math.pi * j / 48), cy + ry * rr * math.sin(2 * math.pi * j / 48),
                              zb + CORE_H * zz)) for j in range(48)])
    ball = k.loft("core_ball", rings[:-1], m[("core", 0x77)], cap_start=False, cap_end=True,
                  end_point=(x0, cy, zb + CORE_H))
    k.smooth(ball, 80)
    q = []
    for v in ball.data.vertices:
        q.append(math.hypot((v.co.x - x0) / rx, (v.co.y - cy) / ry))
    q = np.array(q)
    value = 1.0 - q ** 1.4
    band_split(ball, value, [(lo, m[("core", i)]) for lo, i, _ in CORE_BANDS])
    k.smooth(ball, 80)
    # the ring: a torus round it, flattened
    mid, half, hgt = RING
    pts = []
    for j in range(64):
        a = 2 * math.pi * j / 64
        pts.append((x0 + (rx + mid - 12.0) * math.cos(a), cy + (ry + mid - 12.0) * math.sin(a)))
    verts, faces = [], []
    sec = 10
    for j, (px, py) in enumerate(pts):
        a = 2 * math.pi * j / 64
        dx, dy = math.cos(a), math.sin(a)
        zc = dome_top(fields, px - AXIS, py) - 0.3
        for s in range(sec):
            b = math.pi * s / (sec - 1)
            verts.append(Vector((px + dx * half * -math.cos(b), py + dy * half * -math.cos(b) * ry / rx,
                                 zc + hgt * math.sin(b) + (0.0 if 0 < s < sec - 1 else -0.6))))
    for j in range(64):
        for s in range(sec - 1):
            a0, a1 = j * sec + s, ((j + 1) % 64) * sec + s
            faces.append((a0, a1, a1 + 1, a0 + 1))
    ring = k.mesh_object("core_ring", verts, faces, m[0x05])
    k.recalc_normals(ring)
    k.smooth(ring, 80)
    paint_by_light(ring, RING_BANDS, m)
    return [ball, ring]


def pipe(m, fields):
    """The pipe from the core up the screen out of the picture, its collar, the dark sleeve under it."""
    hw, hh, lift, y0 = PIPE
    x0 = AXIS
    zt = dome_top(fields, 0.0, 66.0)
    axis_z = zt + lift
    rings = []
    for y in np.linspace(y0, 72.0, 12):
        rings.append([Vector((x0 + hw * math.cos(2 * math.pi * j / 32), float(y),
                              axis_z + hh * math.sin(2 * math.pi * j / 32))) for j in range(32)])
    tube = k.loft("pipe", rings, m[("pipe", 0x69)], cap_start=True, cap_end=True,
                  start_point=(x0, y0, axis_z), end_point=(x0, 72.0, axis_z))
    k.smooth(tube, 50)
    paint_by_light(tube, PIPE_BANDS, m, key="pipe")
    collar_rings = []
    for y, s in ((y0 - 0.2, 0.92), (y0 + 0.4, 1.12), (y0 + 2.4, 1.12), (y0 + 3.0, 0.98)):
        collar_rings.append([Vector((x0 + hw * s * math.cos(2 * math.pi * j / 32), y,
                                     axis_z + hh * s * math.sin(2 * math.pi * j / 32))) for j in range(32)])
    collar = k.loft("pipe_collar", collar_rings, m[("pipe", 0x6b)], cap_start=True, cap_end=True,
                    start_point=(x0, y0 - 0.2, axis_z), end_point=(x0, y0 + 3.0, axis_z))
    k.smooth(collar, 50)
    paint_by_light(collar, PIPE_BANDS, m, key="pipe", lift=0.6)
    sw, sh = SLEEVE
    sleeve = mk.box("pipe_sleeve", x0 - sw, x0 + sw, y0 - 2.0, 72.0, zt - 2.0, zt + sh, m[0x05])
    mk.bevel(sleeve, 0.6, 2, 30)
    triangulate([sleeve])
    k.smooth(sleeve, 40)
    paint_by_light(sleeve, RING_BANDS, m, lift=-0.4)
    return [tube, collar, sleeve]


def pods(m):
    """Two dark pods lying side by side on each bay's floor, rounded at their lower ends (under the egg)."""
    off, hw, hh, yend = PODS
    out = []
    for bu in (-BAY_U, BAY_U):
        for s in (-1, 1):
            cx = bu + s * off + AXIS
            prof = [(yend - hw * math.sin(a), hw * math.cos(a)) for a in
                    [math.pi / 2 * (1 - i / 8) for i in range(9)]]
            prof += [(72.5, hw)]
            pts = sorted(prof)
            obj = k.lathe("pod%d%d" % (int(bu), s), pts, m[0x05], segments=20, axis_x=cx, axis_z=Z_BAY + hh * 0.75,
                          squash=hh / hw)
            k.smooth(obj, 60)
            paint_by_light(obj, POD_BANDS, m)
            out.append(obj)
    return out


# --- Shear, cut, export -------------------------------------------------------------------------------------------------

def shear_to_camera(objects):
    for obj in objects:
        mesh = obj.data
        normals = [Vector(cn.vector) for cn in mesh.corner_normals]
        for v in mesh.vertices:
            v.co.y -= v.co.z * TAN_T
        out = [Vector((n.x, n.y, n.z + TAN_T * n.y)).normalized() for n in normals]
        mesh.normals_split_custom_set([tuple(n) for n in out])
        mesh.update()


def cut_open(source, box):
    """The part of an object inside box (x0, x1, y0, y1): bisected, nothing filled (the pieces stay together: their
    cuts are never seen), its normals the uncut object's. None if nothing is inside."""
    x0, x1, y0, y1 = box
    corners = [Vector(c) for c in source.bound_box]
    if (max(c.x for c in corners) <= x0 or min(c.x for c in corners) >= x1 or
            max(c.y for c in corners) <= y0 or min(c.y for c in corners) >= y1):
        return None
    obj = source.copy()
    obj.data = source.data.copy()
    bpy.context.scene.collection.objects.link(obj)
    inside = (min(c.x for c in corners) >= x0 and max(c.x for c in corners) <= x1 and
              min(c.y for c in corners) >= y0 and max(c.y for c in corners) <= y1)
    if inside:
        return obj
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    for co, no in (((x0, 0, 0), (-1, 0, 0)), ((x1, 0, 0), (1, 0, 0)), ((0, y0, 0), (0, -1, 0)),
                   ((0, y1, 0), (0, 1, 0))):
        if not bm.faces:
            break
        bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-6, plane_co=co,
                               plane_no=no, clear_outer=True)
    if not bm.faces:
        bm.free()
        bpy.data.objects.remove(obj)
        return None
    bm.to_mesh(obj.data)
    bm.free()
    shading = mk.NormalSource(source)
    mesh = obj.data
    normals = []
    for poly in mesh.polygons:
        for li in poly.loop_indices:
            n = shading.normal(mesh.vertices[mesh.loops[li].vertex_index].co, poly.center)
            normals.append(tuple(n if n is not None else poly.normal))
    mesh.normals_split_custom_set(normals)
    return obj


def whole_mask(sheet):
    mask = [[False] * W for _ in range(H)]
    for name, sprite, box in PIECES:
        c0, r0 = int(box[0] + OX), int(OY - box[3])
        for r, row in enumerate(k.sprite_mask(sheet, sprite)):
            for c, v in enumerate(row):
                if v:
                    mask[r0 + r][c0 + c] = True
    return mask


def build_whole():
    """The body's pieces and the parts, in the picture's plane: ({piece name: body object}, [parts], materials)."""
    k.reset()
    m = materials()
    fields = Fields()
    bodies = body(m, fields)
    parts = spikes(m, fields)
    parts += dividers(m)
    parts += core(m, fields)
    parts += pipe(m, fields)
    parts += pods(m)
    for obj in parts:
        mk.apply(obj)
    return bodies, parts, m


def build():
    options = k.args()
    out = mk.outdir(options)
    only = options["only"].split(",") if "only" in options else None
    sheet = None
    if "check" in options:
        sheets = options["check"]
        sheet = os.path.join(sheets, "enemy_x25.png") if os.path.isdir(sheets) else sheets
    bodies, parts, m = build_whole()
    whole = list(bodies.values()) + parts
    triangulate(whole)
    bpy.context.scene.view_settings.view_transform = "Standard"
    low, high = mk.bounds(whole)
    print("== whole: %d triangles (body %d), x %.2f..%.2f y %.2f..%.2f z %.2f..%.2f" % (
        mk.triangles(whole), mk.triangles(list(bodies.values())), low.x, high.x, low.y, high.y, low.z, high.z))
    if "stats" in options:
        for obj in sorted(parts, key=lambda o: -mk.triangles([o]))[:10]:
            print("    %-22s %6d" % (obj.name, mk.triangles([obj])))
    mask = whole_mask(sheet) if sheet else None
    if sheet:
        mk.compare("whole, as the camera sees it", mk.coverage(whole, W, H), mask)
    if "whole" in options or "preview" in options or sheet:
        seen = [o.copy() for o in whole]
        for o in seen:
            o.data = o.data.copy()
            bpy.context.scene.collection.objects.link(o)
        shear_to_camera(seen)
        if sheet:
            mk.compare("whole, from straight above", mk.coverage(seen, W, H), mask)
        if "whole" in options:
            mk.export(seen, options["whole"])
        if "preview" in options:
            mk.preview(options["preview"] + "coral_citadel", seen, size=(W, H), scale=5, distance=6.0)
        for o in seen:
            bpy.data.objects.remove(o)
    for name, sprite, box in PIECES:
        if only and name not in only:
            continue
        pieces = [bodies[name].copy()] if name in bodies else []
        for p in pieces:
            p.data = bodies[name].data.copy()
            bpy.context.scene.collection.objects.link(p)
        pieces += [cut_open(src, box) for src in parts]
        pieces = [p for p in pieces if p is not None]
        drop_unused(pieces)
        cx, cy = (box[0] + box[1]) / 2, (box[2] + box[3]) / 2
        mk.transform(pieces, Matrix.Translation((-cx, -cy, 0)))
        bpy.context.view_layer.update()
        triangulate(pieces)
        obj = join(pieces, name)
        obj.data.name = name
        for src in whole:
            src.hide_render = True
        if sheet:
            mk.compare("%s (%% %d), as the camera sees it" % (name, sprite), mk.coverage([obj], 24, 28),
                       k.sprite_mask(sheet, sprite))
        shear_to_camera([obj])
        if sheet:
            mk.compare("%s (%% %d), from straight above" % (name, sprite), mk.coverage([obj], 24, 28),
                       k.sprite_mask(sheet, sprite))
        mk.report(name, [obj], os.path.join(out, name + ".glb"))
        bpy.data.objects.remove(obj)
        for src in whole:
            src.hide_render = False


if __name__ == "__main__":
    build()
