"""GYGES' boss, the great maw (sheet n, written N in the catalogue: 24 2x2 sprites that the level events lay out as one
120 x 168 picture), its maw opening when it fires, its damaged look, and GYGES' two pincers; polished (2026-10-22,
round 35). It replaces wave3_an_boss.py (the boss: blobs of a heightfield painted pixel by pixel, up to 31 pixels tall,
up to 60 materials a piece), wave3_an.py (the pincers: an inflated outline painted pixel by pixel) and
wave3_ar_gyges.py (their frames: those rebuilt with the frames' pixels).

Where it appears: GYGES (episode 2, its end) and REEF (episode 6, the same wave: enemies 1527-1547 are copies of
366-386) put the boss together from 24 sky enemies (366-389; event 15), rows spawned 14 ticks apart (28 pixels, the
scroll's speed): 193 195 197 at x 102 126 150 first (t5289), then 153-161 at x 78 ... 174, 115-123, 77-85, 41 43 45,
3 5 7 last (t5359), as the sheet lays them out: the picture's columns 24-95 for the top two rows and the bottom row,
0-119 for the rest. All 24 share link 110 (the boss bar, event 79): the game kills them together, and as their dlevel
is -1 each switches to its damaged sprite (dgr) when the boss dies and stays as its corpse (enemyAvail 2), so the
damaged look is always the whole beast's. 153 161 193 195 197 have armour 0 (never hit). Event 24 (t5318; REEF t2629)
makes every piece animate for ever (aniactive 1, its cycle restarted together), so the four in the maw's middle (379
380 384 385: 119 121 157 159, ani 9) open and close the maw without pause, in step: 119 229 233 237 241 237 233 229
(and 121 231 235 239 243 ..., 157 267 271 275 279 ..., 159 269 273 277 281 ...); 379 fires (tur 153, freq 45). No
other enemy, launched ones included, shows any of these sprites (frame models are safe).

As the sprites and their 4x upscales draw it (the picture's columns and rows; symmetric about column 63 in coverage,
97 %; lit from the upper left): a huge beast seen from above, its maw down the screen. Its top (rows 2-13) two small
glossy knobs (columns 54-63 and 63-72 of rows 2-11) on a ridge with two slits; its back a carapace of glossy dark
blue-grey lobes (ramp 6), cut straight by the sprites' edges at columns 24 and 95; down its middle a purple spine
(ramp 5; columns 57-69 of rows 12-26) swelling into three warty bulbs (columns 43-84 of rows 27-42, 45-81 of 43-55,
47-80 of 56-78), pale warts on them, dark gaps between them; beside the neck two spiracles, dark holes in purple rims
(columns 38-47 and 79-88 of rows 18-26); great shoulder lobes (rows 56-80, columns 13-45 and their mirror); a
wrinkled face (rows 78-100) with three glowing red eyes each side (columns 35-40, 30-35, 28-32 of rows 79-83, 86-91,
94-99 and their mirror); the maw (columns 35-91 of rows 91-141): a ring of fleshy salmon lips (ramp 4) in lumps, a
fleshy nose hanging from the top lip with a small tooth under it, fangs of bone (ramp 10) leaning in from the ring
(the top lip's two long), a deep red throat ridged in rings (ramp 7); a purple horn either side of the jaw (columns
25-39 of rows 117-134); glossy dark tendrils dripping from the face's sides (rows 96-125), light drops at their
tips; the chin (rows 137-150) with a drip under it.

Built for the game's camera, as GYGES' creatures in their squares of wall are (polish_gyges_wall.py, whose helpers
this imports): the whole beast is one heightfield in the picture's plane (x, y as the sprites draw it, z up), sheared
along the camera's line of sight (y - z tan 20), so that the camera sees every point where the sprites draw it; on a
grid STEP apart whose lines are the pieces' edges, so each piece is the cells of its sprite's box (no mesh cutting),
walled where cut (dark, seen only when a neighbour is missing). Its heights: smooth domes for its parts (MASSES,
mirrored about the axis), joined by a smooth maximum, falling to its outline over FALL; the sprite's dark lines
creased, its fine shading a little relief; the spine's bulbs higher, their warts raised by the sprite's light; the
spiracles and the gaps by the bulbs sunk into dark pits; the maw a ring of lips (a bead over the mouth's outline,
creased between its lumps) round a throat falling deep under the top lip, its rings raised where the sprite draws
them light. Separate solids: the eyes (lenses glowing red in sockets), the fangs (curved cones from the lips' inner
edge leaning into the throat), the tendrils' drops. Painted by the sprite's shades (blurred, LIFT lighter, lighter
where the game's sun lights a face less: COMP, polish_gyges_wall's way), at most 15 materials a piece (the rarest
merged into their neighbours). Heights: z 0 (its underside, the sky's plane) to about 14 (the spine's bulbs, the
lips), the throat's floor at 1: under background 3's plane but for the highest tops (CAMANIS' boss reaches 12.6; the
old maw 31.4, through the player's plane).

The maw's frames (frame models of the four middle pieces): the throat darkens, a fireball swells in it (lumpy, glowing
red to white-hot: 229 a spark, 241 filling the throat's middle) and the top lip's two long fangs fold back (shorter
in each frame); the pieces round them don't change (the frames change only columns 48-95 of rows 93-139, inside the
four), so they meet as the first frame's do.

Its damaged look (dgr): ten damaged sprites are their intact pixels (3 5 7 115 123 153 161 193 195 197: their sprite
lines take the intact models), fourteen are pieces of the damaged whole (51 53 55 of 41 43 45; 87 89 91 93 18 of
77-85; 127 129 131 of 117-121; 165 167 169 of 155-159), which the damaged sprite draws differently (DAMAGED, 2923
pixels): the spine torn open into raw red flesh (columns 44-80 of rows 28-65), the left back gouged (columns 16-40
of rows 28-62), the right shoulder's plating torn off over bare ribs (columns 85-106 of rows 42-75), gashes in the face,
five eyes put out (the lowest right one still burns), the throat dark and bloody, fangs snapped. Built as the intact
beast with its wounds: the heightfield sunk into craters where the damaged sprite shows flesh, bone or holes (WOUND,
faded out over SEAM_FADE towards the pieces that keep their intact look, so that they meet exactly), raw flesh in
them (ramp 7, glowing a little: wet), ribs of bone across the torn shoulder, the put-out eyes dark hollows, the snapped
fangs short.

GYGES' pincers (n 163 above 201, enemies 180 above 181 at x 18; n 11 above 49, enemies 182 above 183 at x 290: ground
enemies at t5304, swaying from side to side while the boss comes in; the right one the left one's pixels mirrored
about column 11): a crab's claw hanging down the screen: an armoured hand (its top cut off by the sprite), the big
fixed finger, broad and curving down into a hooked point, the small movable finger hinged on a glossy blue ball joint
beside it. Their animation (animate 1, for ever) opens the small finger: 163 203 203 203 207 207 207 203 203 203 then
163 ten frames (201 205 245; 11 9 1; 49 47 39): frame models gyges_pincer_203 205 207 245 (left) and 9 47 1 39
(right), the finger turned out about its joint as each frame draws it. Built as solids (lofted shells and tubes),
painted by how they face the game's sun, the right one the left one mirrored about x = -0.5.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera. The boss's whole
has its origin at the picture's middle (60, 84): column c is x = c + 0.5 - 60, row r is y = 83.5 - r; a piece whose
sprite's top left corner is (c0, r0) has its origin at (c0 - 48, 70 - r0) (models.cfg origin). The pincers' origin is
their whole's middle (12, 28): the top piece's at (0, 14), the bottom's at (0, -14).

models.cfg: the model, sprite and frame lines of gyges_maw_* and gyges_pincer_* stay as they are (yaw=0, origin; the
eye glows of 79 83 117 121 131 still sit on the eyes).

Replaces wave3_an_boss.py, wave3_an.py, wave3_ar_gyges.py (all of each: delete them) and wave3_an_kit.py,
wave3_an_art.py (only they read them: delete them), wave3_ar_art.py's MAW_229 ... MAW_241 and CLAW_* (only
wave3_ar_gyges.py read them; its GRYPHON_HEAD_* stay for wave3_ar_beasts.py).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouettes against
enemy_N.png: the boss's outline as the camera sees it, whole and per piece; each pincer piece), --preview <prefix>,
--only <model,...> (or the groups boss, open, damaged, pincers).
"""
import math
import os
import sys

import bpy
import numpy as np
from mathutils import Matrix, Vector, kdtree

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
import polish_machine_kit as mk  # noqa: E402
import polish_gyges_wall as gw  # noqa: E402  (the picture-plane heightfield, its painting, the camera's shear)
from polish_gyges_wall import Pic, parse, blur, fill, dilate, erode, smoothstep, smax, dome, tube  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402
from polish_deli_boss import join, drop_unused  # noqa: E402
from polish_coral_manta import cut  # noqa: E402  (savara's cut, the caps' material set as they are made)

TAN_T = gw.TAN_T
LEFT, TOP = -60.0, 84.0           # the boss's picture in the plane: its top left corner
AXC = 63                          # the axis: the middle of pixel column 63 (column c mirrors 126 - c)
AXIS_X = AXC + 0.5 + LEFT         # 3.5

# The pieces: sprite -> the picture's column and row of its top left corner.
CELLS = {3: (24, 0), 5: (48, 0), 7: (72, 0), 41: (24, 28), 43: (48, 28), 45: (72, 28),
         77: (0, 56), 79: (24, 56), 81: (48, 56), 83: (72, 56), 85: (96, 56),
         115: (0, 84), 117: (24, 84), 119: (48, 84), 121: (72, 84), 123: (96, 84),
         153: (0, 112), 155: (24, 112), 157: (48, 112), 159: (72, 112), 161: (96, 112),
         193: (24, 140), 195: (48, 140), 197: (72, 140)}
# The damaged sprites (dgr) of the pieces whose damaged sprite is their own picture.
DAMAGED_OF = {41: 51, 43: 53, 45: 55, 77: 87, 79: 89, 81: 91, 83: 93, 85: 18, 117: 127, 119: 129, 121: 131,
              155: 165, 157: 167, 159: 169}
MIDDLE = (119, 121, 157, 159)     # the maw's middle pieces, which the frames change
# The maw's frames: frame -> the sprites of the middle pieces (as MIDDLE), the top fangs' length (of the first frame's),
# the fireball's radius and heat (0-1).
FRAMES = {229: ((229, 231, 267, 269), 0.9, 1.4, 0.0), 233: ((233, 235, 271, 273), 0.72, 2.6, 0.35),
          237: ((237, 239, 275, 277), 0.52, 4.2, 0.7), 241: ((241, 243, 279, 281), 0.35, 6.0, 1.0)}


def X(c):
    return c + 0.5 + LEFT


def Y(r):
    return TOP - r - 0.5


def box_of(sprite):
    c0, r0 = CELLS[sprite]
    return (c0 + LEFT, c0 + LEFT + 24.0, TOP - r0 - 28.0, TOP - r0)


def cols_rows(Xa, Ya):
    """Points of the plane as the picture's (fractional) column and row indices (a pixel's middle at c, r)."""
    return np.asarray(Xa, float) - LEFT - 0.5, TOP - 0.5 - np.asarray(Ya, float)


def mirrored(items, col_index=0):
    """A list of specs whose element col_index is a column, with each one off the axis mirrored too."""
    out = []
    for it in items:
        out.append(it)
        c = it[col_index]
        if abs(c - AXC) > 0.01:
            m = list(it)
            m[col_index] = 2 * AXC - c
            out.append(tuple(m))
    return out


# --- The pictures ----------------------------------------------------------------------------------------------------

def patched(base_rows, patch_text):
    """A copy of a picture's rows (lists of indices, None none) with a patch's runs ('row:column:hex') put in."""
    rows = [list(r) for r in base_rows]
    for item in patch_text.split():
        r, c, hx = item.split(":")
        r, c = int(r), int(c)
        for i in range(len(hx) // 2):
            v = hx[2 * i:2 * i + 2]
            while len(rows) <= r:
                rows.append([None] * 120)
            rows[r][c + i] = None if v == ".." else int(v, 16)
    return rows


def boss_rows(look="intact"):
    rows = parse(BOSS)
    while len(rows) < 168:
        rows.append([None] * 120)
    if look == "damaged":
        rows = patched(rows, DAMAGED)
    elif look in FRAMES:
        rows = patched(rows, globals()["OPEN_%d" % look])
    return rows


def body_mask(pic):
    """The beast's pixels: its coverage with its holes closed (slits, the spiracles, the gaps by the spine, between
    the teeth) and the strays left out (the clipped tips beyond the sprites at rows 56-57, a dot by the chin)."""
    m = pic.a >= 0
    keep = np.zeros_like(m)
    # The main body: flood from its middle.
    stack = [(84, 63)]
    keep[84, 63] = True
    h, w = m.shape
    while stack:
        r, c = stack.pop()
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            rr, cc = r + dr, c + dc
            if 0 <= rr < h and 0 <= cc < w and m[rr, cc] and not keep[rr, cc]:
                keep[rr, cc] = True
                stack.append((rr, cc))
    # Its holes: what the outside can't reach.
    outside = np.zeros_like(m)
    stack = [(r, c) for r in range(h) for c in (0, w - 1) if not keep[r, c]] + \
            [(r, c) for c in range(w) for r in (0, h - 1) if not keep[r, c]]
    for r, c in stack:
        outside[r, c] = True
    while stack:
        r, c = stack.pop()
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            rr, cc = r + dr, c + dc
            if 0 <= rr < h and 0 <= cc < w and not keep[rr, cc] and not outside[rr, cc]:
                outside[rr, cc] = True
                stack.append((rr, cc))
    body = ~outside
    # The back's top corners, cut square by the sprites' edges (columns 24 and 95 from row 14), rounded off.
    rows, cols = np.mgrid[0:h, 0:w]
    for cc, rc, rad in BACK_CORNERS:
        corner = ((cols - cc) * np.sign(cc - AXC) > 0) & (rows < rc)
        body &= ~(corner & (np.hypot(cols - cc, rows - rc) > rad))
    return body


class Shape:
    """A mask of the picture as a smooth shape (polish_gyges_wall.Region's, its distances by a k-d tree): its outline
    the 0.5 contour of the mask blurred by sigma; depth(): how far a point lies inside it (negative: outside)."""

    def __init__(self, pic, mask, sigma=0.55, step=0.25):
        self.pic = pic
        self.soft = blur(mask.astype(float), sigma)
        xs = np.arange(pic.left + step / 2, pic.left + pic.w, step)
        ys = np.arange(pic.top - pic.h + step / 2, pic.top, step)
        Xg, Yg = np.meshgrid(xs, ys)
        inside = pic.sample(self.soft, Xg, Yg) > 0.5
        p = np.pad(inside, 1, mode="edge")
        h, w = inside.shape
        edge = np.zeros_like(inside)
        for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            edge |= p[1 + dr:1 + dr + h, 1 + dc:1 + dc + w] != inside
        pts = np.stack([Xg[edge], Yg[edge]], 1)
        self.tree = kdtree.KDTree(len(pts))
        for i, (px, py) in enumerate(pts):
            self.tree.insert((float(px), float(py), 0.0), i)
        self.tree.balance()

    def inside(self, Xa, Ya):
        pic = self.pic
        Xa, Ya = np.asarray(Xa, float), np.asarray(Ya, float)
        within = (Xa >= pic.left) & (Xa <= pic.left + pic.w) & (Ya <= pic.top) & (Ya >= pic.top - pic.h)
        return within & (pic.sample(self.soft, Xa, Ya) > 0.5)

    def depth(self, Xa, Ya):
        Xa, Ya = np.asarray(Xa, float), np.asarray(Ya, float)
        flat = np.stack([Xa.ravel(), Ya.ravel()], 1)
        d = np.array([self.tree.find((float(px), float(py), 0.0))[2] for px, py in flat]).reshape(Xa.shape)
        return np.where(self.inside(Xa, Ya), d, -d)


# --- The beast's heights ---------------------------------------------------------------------------------------------

# Its masses (the left half's, mirrored): middle (column, row), radii (columns, rows), height, angle, power.
MASSES = [
    ((58.6, 6.6), (5.0, 4.6), 9.6, 0.0, 0.5),          # the knobs at its top
    ((63.0, 11.5), (17.0, 4.2), 8.4, 0.0, 0.55),       # the ridge they stand on
    ((48.5, 19.0), (10.5, 8.0), 10.6, -10.0, 0.5),     # the back's upper lobes
    ((31.0, 23.0), (8.0, 9.5), 8.6, 0.0, 0.5),
    ((34.0, 42.0), (11.5, 15.0), 10.4, 0.0, 0.5),      # the back's big lobes
    ((44.0, 52.0), (8.0, 6.0), 9.0, 0.0, 0.5),
    ((34.0, 66.0), (20.5, 12.5), 11.4, -8.0, 0.5),     # the shoulders
    ((19.5, 73.5), (8.5, 9.5), 8.2, 0.0, 0.5),
    ((63.0, 87.5), (40.0, 12.0), 10.4, 0.0, 0.55),     # the face
    ((35.0, 92.0), (15.0, 10.0), 10.0, 0.0, 0.5),
    ((20.0, 100.0), (10.0, 10.5), 7.0, 0.0, 0.5),      # the face's outer edge
    ((34.0, 114.0), (11.0, 13.0), 8.6, 0.0, 0.5),      # the cheeks
    ((63.0, 126.0), (29.0, 17.0), 8.6, 0.0, 0.5),      # the jaw
    ((63.0, 143.0), (22.0, 6.5), 6.0, 0.0, 0.5),       # the chin
]
# The spine: the neck and three bulbs (on the axis): middle (column, row), radii, height, power.
SPINE = [((63.0, 18.5), (6.8, 9.0), 10.6, 0.5),
         ((63.0, 34.5), (21.0, 8.4), 12.6, 0.45),
         ((63.0, 49.0), (18.0, 6.6), 12.2, 0.45),
         ((63.0, 66.5), (16.5, 11.5), 13.0, 0.45)]
WARTS = 0.9                       # the spine's warts: raised this much where the sprite's purple is lightest
# The spiracles beside the neck: middle (column, row), radii, how deep their pit, the rim's height over the back.
SPIRACLES = [((42.6, 22.6), (4.6, 2.9), 4.0, 1.0)]
FALL = 2.6                        # how far in from its outline the beast rises to its full height
BACK_FALL = (6.0, 24.5, 94.5)     # but its back's flanks (cut straight by the sprites' edges at these columns) over
BACK_CORNERS = [(31.0, 21.0, 7.5), (88.0, 21.0, 7.5)]   # the back's top corners rounded: middle (column, row), radius
CREASE = (1.9, 0.9, 78.0)         # the sprite's dark lines inside it cut this deep (on its full height): over the back
                                  # and the shoulders, and from this row on (the wrinkled face: shallower)
DETAIL = (0.07, 0.3)              # its fine shading as relief: per shade, its limit
PIT = 1.2                         # the closed holes (slits, the gaps by the bulbs): their floor

# The maw: the half-width of its outline (pixels from the axis) by row.
MOUTH_W = {91: 10, 92: 11, 93: 12, 94: 12, 95: 16, 96: 17, 97: 18.5, 98: 20, 99: 20.5, 100: 21, 101: 22, 102: 26,
           103: 27, 104: 28, 105: 28, 106: 28, 107: 28, 108: 28, 109: 28, 110: 27, 111: 26, 112: 26, 113: 25, 114: 24,
           115: 23.5, 116: 24, 117: 24, 118: 24, 119: 23, 120: 22, 121: 21, 122: 19.5, 123: 19, 124: 19, 125: 19,
           126: 18, 127: 18, 128: 18, 129: 18, 130: 18, 131: 17, 132: 17, 133: 17, 134: 17, 135: 17, 136: 17, 137: 17,
           138: 14, 139: 12, 140: 12, 141: 7}
LIP_W = 5.2                       # the lips' ring: this wide inside the maw's outline
LIP_H = (1.4, 3.0)                # its bead over the face round it: height, and more where the sprite draws it light
THROAT = (1.0, 6.4)               # the throat's floor: at its deepest point, at the lips' inner edge
DEEP = (63.0, 104.0)              # the deepest point, under the top lip
RINGS = 0.9                       # the throat's rings: raised this much where the sprite draws them light
RING_CUT = (1.15, 2.1, 3.0)       # and painted: black under the first, then 0x72, 0x74, 0x76 (the blurred red + 1)

# The purple horns either side of the jaw (the left one; mirrored), curving down and out to a point: points (column,
# row, half-width, height).
HORN = [(36.4, 119.4, 1.3, 7.6), (34.8, 122.4, 2.6, 9.0), (33.2, 125.4, 3.4, 9.6), (31.2, 128.0, 2.8, 9.0),
        (29.4, 130.0, 1.6, 8.0), (27.8, 131.8, 0.5, 6.6)]
# The nose hanging from the top lip into the maw: points (column, row, half-width, height).
NOSE = [(63.0, 91.5, 3.4, 10.6), (63.0, 95.0, 3.0, 10.2), (63.0, 98.0, 2.2, 9.0), (63.0, 100.4, 1.3, 7.6)]
# The fangs (the left ones; mirrored, but the one on the axis): base (column, row), tip (column, row), radius at the
# base, how far the tip hangs under the base, how much the fang arches (its middle raised).
TEETH = [((55.8, 96.6), (58.4, 108.0), 2.4, 5.0, 1.2),      # the top lip's long fang
         ((46.8, 101.4), (51.6, 106.8), 2.1, 3.0, 0.8),
         ((41.0, 109.2), (49.6, 112.2), 2.0, 3.0, 0.8),
         ((41.4, 115.4), (47.8, 116.0), 1.5, 2.0, 0.6),
         ((44.0, 121.0), (49.8, 118.2), 1.8, 2.2, 0.6),
         ((46.6, 128.4), (53.6, 124.4), 1.8, 2.4, 0.6),
         ((51.8, 136.8), (55.2, 130.4), 1.9, 2.4, 0.7),
         ((59.6, 138.4), (60.0, 131.2), 1.7, 2.0, 0.6)]
TOOTH_AXIS = ((63.0, 100.4), (63.0, 105.4), 1.2, 2.0, 0.3)   # the small one under the nose

# The damaged look: the eye that still burns (the lowest right one), the fangs snapped (how much of each is left).
LIT_WHEN_DAMAGED = (2, 1)
BROKEN = {"tooth0_m": 0.28, "tooth_axis": 0.5, "tooth6_m": 0.55, "tooth7": 0.35, "tooth7_m": 0.5}

# Eyes (the left ones; mirrored): middle (column, row), radii (columns, rows).
EYES = [((37.6, 81.0), (2.3, 2.0)), ((32.6, 88.6), (2.3, 2.1)), ((30.0, 96.6), (2.0, 2.1))]
EYE_SOCKET = 1.6


def mouth_mask():
    m = np.zeros((168, 120), bool)
    for r, hw in MOUTH_W.items():
        c0, c1 = int(math.ceil(AXC - hw - 0.01)), int(math.floor(AXC + hw + 0.01))
        m[r, c0:c1 + 1] = True
    return m


class Beast:
    """The beast's heightfield of one look (its picture pic): heights(X, Y) over the sky's plane, and what paints it."""

    def __init__(self, pic, intact=None, wounded=False):
        self.pic = pic
        self.intact = intact or pic     # the intact picture (the shapes follow it; a look only repaints and wounds)
        ip = self.intact
        self.wounds = Wounds(pic, ip) if wounded else None
        self.body = body_mask(ip)
        self.shape = Shape(ip, self.body, sigma=0.6)
        dark = ip.any(0x00, 0x01)
        holes = self.body & (ip.a < 0)
        self.holes_soft = blur(holes.astype(float), 0.55)
        # The dark lines inside the beast (outline pixels with the beast all round).
        h, w = dark.shape
        p = np.pad(self.body, 1)
        surrounded = np.ones_like(dark)
        for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            surrounded &= p[1 + dr:1 + dr + h, 1 + dc:1 + dc + w]
        self.internal = (dark | holes) & surrounded
        rows = np.arange(ip.h)[:, None] + np.zeros((1, ip.w))
        # On the back the lobes are parted by the darkest blue too.
        self.internal |= ip.any(0x60) & surrounded & (rows < CREASE[2])
        self.crease = blur(self.internal.astype(float), 0.6)
        shade = np.where(ip.a >= 0, ip.a & 15, 0).astype(float)
        lit = self.body & ~dark & (ip.a >= 0)
        self.soft = blur(fill(shade, lit), 0.6)
        self.broad = blur(fill(shade, lit), 2.2)
        self.mouth = mouth_mask()
        self.mouth_shape = Shape(ip, self.mouth, sigma=0.8)
        purple = ip.ramp(5)
        self.purple_light = blur(np.where(purple, shade, 0.0), 0.5)
        throat = ip.ramp(7) & self.mouth
        self.throat_light = blur(np.where(throat, shade, 0.0), 0.6)
        lips = ip.ramp(4)
        self.lips_light = blur(np.where(lips, shade, 0.0), 0.7)

    def masses(self, Xa, Ya):
        c, r = cols_rows(Xa, Ya)
        cm = AXC - np.abs(c - AXC)            # the left half's column
        xm, ym = X(cm), Ya
        out = np.zeros_like(xm)
        for (mc, mr), (rc, rr), hgt, ang, pw in MASSES:
            out = smax(out, dome(xm, ym, (X(mc), Y(mr)), (rc, rr), hgt, ang, pw), 2.0)
        for (mc, mr), (rc, rr), hgt, pw in SPINE:
            out = smax(out, dome(xm, ym, (X(mc), Y(mr)), (rc, rr), hgt, 0.0, pw), 1.4)
        return out

    def heights(self, Xa, Ya):
        ip = self.intact
        Xa, Ya = np.asarray(Xa, float), np.asarray(Ya, float)
        c, r = cols_rows(Xa, Ya)
        cm = AXC - np.abs(c - AXC)
        h = self.masses(Xa, Ya)
        depth = self.shape.depth(Xa, Ya)
        flank = (r > 12.0) & (r < 57.0) & ((c < BACK_FALL[1] + BACK_FALL[0]) | (c > BACK_FALL[2] - BACK_FALL[0]))
        edge = np.minimum(c - BACK_FALL[1], BACK_FALL[2] - c)
        fall = np.where(flank, np.clip(BACK_FALL[0] - (BACK_FALL[0] - FALL) * smoothstep(0.0, 4.0, np.abs(
            r - 34.5) - 18.0), FALL, BACK_FALL[0]), FALL)
        h = h * smoothstep(0.0, 1.0, depth / fall) ** 0.8
        del edge
        # The spine's warts.
        h = h + WARTS * np.clip(ip.sample(self.purple_light, Xa, Ya) - 4.0, 0.0, 6.0) / 6.0 * 1.6
        # The sprite's fine shading as relief, its dark lines creased.
        fine = ip.sample(self.soft, Xa, Ya) - ip.sample(self.broad, Xa, Ya)
        h = h + np.clip(DETAIL[0] * fine, -DETAIL[1], DETAIL[1]) * smoothstep(0.5, 2.0, h)
        crease = CREASE[1] + (CREASE[0] - CREASE[1]) * smoothstep(CREASE[2] + 2.0, CREASE[2] - 2.0, r)
        h = h - crease * ip.sample(self.crease, Xa, Ya) * np.clip(h / 4.0, 0.0, 1.0)
        # The closed holes: pits.
        hole = smoothstep(0.25, 0.6, ip.sample(self.holes_soft, Xa, Ya))
        h = h * (1.0 - hole) + PIT * hole
        # The spiracles.
        for (sc, sr), (rx, ry), deep, rim in SPIRACLES:
            d = np.sqrt(((cm - sc) / rx) ** 2 + ((r - sr) / ry) ** 2)
            h = h + rim * np.exp(-((d - 1.15) / 0.3) ** 2) - deep * smoothstep(1.05, 0.55, d)
        # The eyes' sockets.
        for (ec, er), (rx, ry) in EYES:
            d = np.sqrt(((cm - ec) / (rx + 0.8)) ** 2 + ((r - er) / (ry + 0.8)) ** 2)
            h = h - EYE_SOCKET * smoothstep(1.0, 0.4, d)
        # The maw.
        md = self.mouth_shape.depth(Xa, Ya)
        face = h
        lip_light = ip.sample(self.lips_light, Xa, Ya)
        bead = LIP_H[0] + LIP_H[1] * np.clip(lip_light - 2.5, 0.0, 6.0) / 6.0
        u = np.clip(md / LIP_W, 0.0, 1.0)
        lip = face + bead * np.sin(np.pi * np.clip(u * 0.85 + 0.075, 0.0, 1.0)) ** 0.7
        # The throat, falling towards its deepest point under the top lip.
        sd = np.sqrt(((c - DEEP[0]) / 26.0) ** 2 + ((r - DEEP[1]) / np.where(r > DEEP[1], 34.0, 10.0)) ** 2)
        floor = THROAT[0] + (THROAT[1] - THROAT[0]) * np.clip(sd, 0.0, 1.0) ** 1.4
        floor = floor + RINGS * np.clip(ip.sample(self.throat_light, Xa, Ya) - 0.5, 0.0, 3.0) / 3.0
        t = smoothstep(LIP_W - 0.6, LIP_W + 1.2, md)
        mouth_h = lip * (1.0 - t) + floor * t
        h = np.where(md > 0.0, np.minimum(np.maximum(mouth_h, 0.0) + 0.0, np.maximum(lip, floor)), h)
        # The fleshy nose hanging from the top lip.
        nose = tube(Xa, Ya, [(X(c_), Y(r_), w_, z_) for c_, r_, w_, z_ in NOSE])
        h = np.where(nose > 0.0, np.maximum(h, nose), h)
        # The horns.
        horn = tube(X(cm), Ya, [(X(c_), Y(r_), w_, z_) for c_, r_, w_, z_ in HORN], power=0.6)
        h = np.where(horn > 0.0, smax(h, horn, 0.6), h)
        if self.wounds is not None:
            h = self.wounds.apply(h, Xa, Ya)
        return np.maximum(h, 0.0)

    def cells(self, Xa, Ya):
        return self.shape.inside(Xa, Ya)


# --- The damaged look: wounds --------------------------------------------------------------------------------------

DENT = 3.4                        # the wounds: sunk this deep into the beast (flesh and holes), with noise
HOLE = 2.4                        # the black holes in them: this much deeper
RIB = (1.6, 1.0)                  # the bare ribs over the torn shoulder: how high over the wound's floor, more by shade
GORE = 0.9                        # the raw flesh: lumps this high where the sprite draws it light
SEAM_FADE = (0.4, 2.2)            # the wounds fade out towards the pieces that keep their intact look (0 within 0.4)
# The edges between pieces that switch to damaged sprites of their own and those whose damaged sprite is their intact
# one (row 28 under 3 5 7, row 140 over 193 195 197, columns 24 and 96 beside 115 123 153 161, row 84 under 77 and 85
# over 115 and 123): segments (x0, y0, x1, y1).
SEAMS = [(-36.0, 56.0, 36.0, 56.0), (-36.0, -56.0, 36.0, -56.0), (-36.0, 0.0, -36.0, -56.0), (36.0, 0.0, 36.0, -56.0),
         (-60.0, 0.0, -36.0, 0.0), (36.0, 0.0, 60.0, 0.0)]


class Wounds:
    """Where the damaged picture tore the beast open: it differs from the intact one there and shows flesh (ramp 7),
    bone (ramp 10) or black, outside the maw and the eyes."""

    def __init__(self, pic, intact):
        self.pic = pic
        a, b = intact.a, pic.a
        changed = (a != b) & (b >= 0)
        flesh = changed & pic.ramp(7)
        bone = changed & pic.ramp(10)
        black = changed & pic.any(0x00, 0x01, 0x60)
        torn = flesh | bone | black
        mouth = mouth_mask()
        eyes = np.zeros_like(torn)
        rows, cols = np.mgrid[0:a.shape[0], 0:a.shape[1]]
        for (ec, er), (rx, ry) in EYES:
            for c in (ec, 2 * AXC - ec):
                eyes |= ((cols - c) / (rx + 2.0)) ** 2 + ((rows - er) / (ry + 2.0)) ** 2 < 1.0
        keep = ~dilate(mouth, 1) & ~eyes
        self.torn = torn & keep
        self.torn_soft = blur(erode(dilate(self.torn, 1), 1).astype(float), 1.0)
        self.black_soft = blur((black & keep).astype(float), 0.6)
        self.bone = bone & keep
        self.bone_soft = blur(self.bone.astype(float), 0.5)
        self.bone_shade = blur(fill(np.where(b >= 0, b & 15, 0).astype(float), self.bone), 0.6)
        self.flesh_shade = blur(fill(np.where(b >= 0, b & 15, 0).astype(float), flesh & keep), 0.7)
        self.put_out = [(c, er, rx, ry) for i, ((ec, er), (rx, ry)) in enumerate(EYES)
                        for side, c in ((0, ec), (1, 2 * AXC - ec)) if (i, side) != LIT_WHEN_DAMAGED]

    def fade(self, Xa, Ya):
        d = np.full(np.shape(Xa), 1e9)
        for x0, y0, x1, y1 in SEAMS:
            dx, dy = x1 - x0, y1 - y0
            t = np.clip(((Xa - x0) * dx + (Ya - y0) * dy) / (dx * dx + dy * dy), 0.0, 1.0)
            d = np.minimum(d, np.hypot(Xa - (x0 + t * dx), Ya - (y0 + t * dy)))
        return smoothstep(SEAM_FADE[0], SEAM_FADE[1], d)

    def amount(self, Xa, Ya):
        return smoothstep(0.2, 0.7, self.pic.sample(self.torn_soft, Xa, Ya)) * self.fade(Xa, Ya)

    def apply(self, h, Xa, Ya):
        pic = self.pic
        w = self.amount(Xa, Ya)
        noise = np.sin(Xa * 1.7 + 0.6) * np.sin(Ya * 1.3 + 1.1) * 0.5 + np.sin(Xa * 0.9 - Ya * 1.1) * 0.35
        floor = np.maximum(h - DENT * (1.0 + 0.25 * noise), 1.0)
        floor = floor - HOLE * smoothstep(0.35, 0.8, pic.sample(self.black_soft, Xa, Ya))
        floor = floor + GORE * np.clip(pic.sample(self.flesh_shade, Xa, Ya) - 2.0, 0.0, 5.0) / 5.0
        rib = smoothstep(0.3, 0.75, pic.sample(self.bone_soft, Xa, Ya))
        floor = floor + rib * (RIB[0] + RIB[1] * np.clip(pic.sample(self.bone_shade, Xa, Ya) - 6.0, 0.0, 6.0) / 6.0)
        floor = np.maximum(floor, 0.4)
        h = h * (1.0 - w) + floor * w
        c, r = cols_rows(Xa, Ya)
        fade = self.fade(Xa, Ya)
        for ec, er, rx, ry in self.put_out:      # the put-out eyes: dark hollows
            d = np.sqrt(((c - ec) / (rx + 0.4)) ** 2 + ((r - er) / (ry + 0.4)) ** 2)
            h = h - 1.6 * smoothstep(1.0, 0.3, d) * fade
        return h


# --- The maw's fire --------------------------------------------------------------------------------------------------

FIRE = (63.0, 112.0)              # the fireball's middle (column, row), low in the throat
FIRE_SHADES = [(0x75, 0.36), (0x77, 0.42), (0x79, 0.48), (0x7b, 0.55), (0x7d, 0.6), (0x7f, 0.65)]


def lumpy(name, centre, radii, seed, amount=0.22, count=10, around=24):
    """An ellipsoid lofted from explicit rings, its surface pushed in and out by smooth noise (the same every run)."""
    from mathutils import noise as mnoise
    (cx, cy, cz), (rx, ry, rz) = centre, radii
    rings = []
    off = Vector((seed * 3.1, seed * 1.7, seed * 2.3))
    for i in range(1, count):
        p = -math.pi / 2 + math.pi * i / count
        ring_pts = []
        for j in range(around):
            a = 2 * math.pi * j / around
            d = Vector((math.cos(p) * math.cos(a), math.cos(p) * math.sin(a), math.sin(p)))
            f = 1.0 + amount * mnoise.noise(d * 1.6 + off)
            ring_pts.append(Vector((cx + rx * d.x * f, cy + ry * d.y * f, cz + rz * d.z * f)))
        rings.append(ring_pts)
    obj = k.loft(name, rings, None, cap_start=True, cap_end=True, start_point=(cx, cy, cz - rz),
                 end_point=(cx, cy, cz + rz * (1.0 + amount * mnoise.noise(Vector((0, 0, 1.6)) + off))))
    k.smooth(obj, 80)
    return obj


def fire_parts(beast, radius, heat):
    """The fireball swelling in the throat: lumpy, red at its flanks, orange to white-hot over its crown and inside
    (heat 0-1 makes it hotter)."""
    x, y = X(FIRE[0]), Y(FIRE[1])
    z = surface(beast, x, y) + radius * 0.55
    parts = []
    ball = lumpy("fire", (x, y, z), (radius, radius * 0.92, radius * 0.75), 7, amount=0.24)
    centres, normals = gw.face_data(ball)
    up = normals[:, 2] * 0.75 + normals[:, 0] * -0.25 + normals[:, 1] * 0.25
    level = np.clip(0.2 + 1.2 * heat + 1.4 * up, 0, 2).astype(int)
    parts.append(Part(ball, [("fire",) + FIRE_SHADES[i] for i in level], (x, y)))
    if radius > 2.5:      # its white-hot heart breaking through its crown
        core = lumpy("fire_core", (x - radius * 0.12, y + radius * 0.15, z + radius * 0.32),
                     (radius * 0.42, radius * 0.38, radius * 0.4), 3, amount=0.2, count=8, around=18)
        i = min(len(FIRE_SHADES) - 1, int(round(3 + 2 * heat)))
        parts.append(Part(core, [("fire",) + FIRE_SHADES[i]] * len(core.data.polygons), (x, y)))
    return parts


# --- Painting --------------------------------------------------------------------------------------------------------

# The beast's colours: per ink (a ramp of the sprite), the shades it is painted in, its finish (metallic, roughness)
# and glows (index: emission strength).
INKS = {
    "body": (6, [0x61, 0x62, 0x63, 0x64, 0x65, 0x66, 0x67, 0x69, 0x6b], (0.25, 0.3), {}),
    "purple": (5, [0x52, 0x54, 0x56, 0x58, 0x5b], (0.2, 0.34), {}),
    "lips": (4, [0x43, 0x45, 0x47, 0x49, 0x4b], (0.05, 0.42), {}),
    "throat": (7, [0x70, 0x72, 0x74, 0x76], (0.0, 0.85), {0x70: (0x74, 0.02), 0x72: (0x76, 0.22), 0x74: 0.3,
                                                         0x76: 0.34}),
    "flesh": (7, [0x71, 0x73, 0x75, 0x77], (0.0, 0.3), {0x71: (0x74, 0.12), 0x73: 0.2, 0x75: 0.28, 0x77: 0.34}),
    "bone": (10, [0xa4, 0xa7, 0xa9, 0xab, 0xad], (0.05, 0.32), {}),
}
DARK = 0x60
LIFT = 1.2
INK_LIFT = {"bone": 1.6}           # the bare ribs a little paler still (they read brown from the game's camera)
COMP = 2.0
LIT_MEAN = 0.72


def pal(prefix, index, metallic, roughness, glow=0.0):
    """A palette material; glow: its emission strength in its own colour, or (palette index, strength) to glow in
    another shade of it (a dark red that glows a brighter red)."""
    if isinstance(glow, tuple):
        source, strength = glow
    else:
        source, strength = index, glow
    extra = dict(emission=k.level_palette()[source], emission_strength=strength) if strength > 0 else {}
    return k.material("%s_%x" % (prefix, index), palette=index, metallic=metallic, roughness=roughness, **extra)


def mat_of(key):
    """The material of a paint key: (ink, index), 'dark', ('glow', index, strength) ..."""
    if key == "dark":
        return pal("maw", DARK, 0.2, 0.4)
    kind = key[0]
    if kind in INKS:
        _, _, (met, rough), glows = INKS[kind]
        return pal("maw_" + kind, key[1], met, rough, glows.get(key[1], 0.0))
    if kind == "glow":
        return pal("maw_glow", key[1], 0.0, 0.2, key[2])
    if kind == "fire":
        return pal("maw_fire", key[1], 0.0, 0.4, key[2])
    raise ValueError(key)


class Paint:
    """How a look paints the beast: each ink's pixels (blurred weights) and shades (filled, blurred)."""

    def __init__(self, beast):
        pic = beast.pic
        self.pic, self.beast = pic, beast
        shade = np.where(pic.a >= 0, pic.a & 15, 0).astype(float)
        self.inks = []
        for name, (ramp, shades, _, _) in INKS.items():
            mask = pic.ramp(ramp)
            if name == "bone":       # the fangs are solids of their own: only the bare ribs in the wounds
                mask = mask & beast.wounds.bone if beast.wounds is not None else mask & False
            if not mask.any():
                continue
            self.inks.append((name, shades, blur(mask.astype(float), 0.6), blur(fill(shade, mask), 0.8)))
        self.dark = blur((pic.any(0x00, 0x01) | (beast.body & (pic.a < 0))).astype(float), 0.7)
        # The throat's rings: the look's red there (its shade, 0 where it draws black), blurred.
        self.rings = blur(np.where(pic.ramp(7) & beast.mouth, shade + 1.0, 0.0), 0.55)
        if beast.wounds is not None:
            mask = beast.wounds.torn & pic.ramp(7)
            self.inks.append(("flesh", INKS["flesh"][1], blur(mask.astype(float), 0.6) * 1.2,
                              blur(fill(shade, mask), 0.7)))

    def keys(self, Xa, Ya, normals):
        pic = self.pic
        lit_by = gw.sun_on(normals)
        weights = np.stack([pic.sample(w, Xa, Ya) for _, _, w, _ in self.inks], 0)
        which = weights.argmax(0)
        dark = pic.sample(self.dark, Xa, Ya)
        per = []
        for name, shades, _, soft in self.inks:
            s = pic.sample(soft, Xa, Ya) + LIFT + INK_LIFT.get(name, 0.0) + COMP * (LIT_MEAN - lit_by)
            per.append(gw.nearest(s, shades))
        md = self.beast.mouth_shape.depth(Xa, Ya)
        in_throat = md > LIP_W - 0.4
        names = [ink[0] for ink in self.inks]
        # In the maw only the lips and the throat (what the sprite draws there besides them is the fangs).
        mouth_only = np.array([n in ("lips", "throat") for n in names])
        if self.beast.wounds is not None:   # outside the wounds no raw flesh; in them no throat
            torn = self.beast.wounds.amount(Xa, Ya) > 0.3
            for j, n in enumerate(names):
                if n == "flesh":
                    weights[j] = np.where(torn, weights[j], -1.0)
                elif n == "throat":
                    weights[j] = np.where(torn, -1.0, weights[j])
            which = weights.argmax(0)
        which_mouth = np.where(mouth_only[:, None], weights, -1.0).argmax(0)
        rings = pic.sample(self.rings, Xa, Ya)
        out = []
        for i in range(len(Xa)):
            w = which_mouth[i] if md[i] > 0.6 else which[i]
            if in_throat[i] and names[w] == "throat":
                # the throat: black between its rings, the rings red (the brighter, the more the sprite lights them)
                t = rings[i]
                out.append(("throat", 0x70 if t < RING_CUT[0] else 0x72 if t < RING_CUT[1] else 0x74 if
                            t < RING_CUT[2] else 0x76))
            elif dark[i] > 0.62 or (md[i] > 0.6 and weights[w, i] < 0.08):
                out.append(("throat", 0x70) if in_throat[i] else "dark")
            else:
                out.append((names[w], int(per[w][i])))
        return out


def limit_materials(keys, limit=15):
    """Merges paint keys into their nearest shade of the same ink until at most `limit` are left: the rarest shade of
    the ink that has the most shades first (so no ink loses all its middle shades)."""
    keys = list(keys)
    while True:
        used = {}
        for key in keys:
            used[key] = used.get(key, 0) + 1
        if len(used) <= limit:
            return keys
        per_ink = {}
        for key in used:
            if isinstance(key, tuple) and key[0] in INKS:
                per_ink.setdefault(key[0], []).append(key)
        ink = max(per_ink, key=lambda name: (len(per_ink[name]), name))
        rarest = min(per_ink[ink], key=lambda key: (used[key], str(key)))
        same = [o for o in per_ink[ink] if o != rarest]
        to = min(same, key=lambda o: (abs((o[1] & 15) - (rarest[1] & 15)), -used[o]))
        keys = [to if key == rarest else key for key in keys]


def assign(parts):
    """Gives a piece's parts (object, its faces' paint keys) their materials: at most 15 in all, in a fixed order."""
    flat = [key for _, keys in parts for key in keys]
    flat = limit_materials(flat)
    order = sorted(set(flat), key=lambda key: str(key))
    slot = {key: i for i, key in enumerate(order)}
    mats = [mat_of(key) for key in order]
    i = 0
    for obj, keys in parts:
        mesh = obj.data
        mesh.materials.clear()
        for m in mats:
            mesh.materials.append(m)
        n = len(keys)
        mesh.polygons.foreach_set("material_index", [slot[key] for key in flat[i:i + n]])
        i += n
        mesh.update()


def plate_keys(obj, kinds, paint):
    centres, normals = gw.face_data(obj)
    top_keys = paint.keys(centres[:, 0], centres[:, 1], normals)
    return [top_keys[i] if kinds[i] == 0 else "dark" for i in range(len(kinds))]


# --- Separate parts --------------------------------------------------------------------------------------------------

class Part:
    """A separate solid of the beast: its object, its faces' paint keys and the point that says which piece holds it."""

    def __init__(self, obj, keys, anchor):
        self.obj, self.keys, self.anchor = obj, keys, anchor


def surface(beast, x, y):
    return float(beast.heights(np.array([x]), np.array([y]))[0])


def eye_parts(beast, lit=None):
    """The eyes: glowing red lenses in their sockets; lit(i, side) False: put out (none)."""
    parts = []
    for i, ((ec, er), (rx, ry)) in enumerate(EYES):
        for side, c in ((0, ec), (1, 2 * AXC - ec)):
            if lit is not None and not lit(i, side):
                continue
            x, y = X(c), Y(er)
            z = surface(beast, x, y)
            body = gw.ellipsoid("eye%d_%d" % (i, side), (x, y, z - 0.35), (rx, ry, 1.1), None, count=8, around=24)
            core = gw.ellipsoid("eye%d_%d_core" % (i, side), (x - 0.25 if side == 0 else x + 0.25, y + 0.2, z + 0.45),
                                (rx * 0.5, ry * 0.5, 0.35), None, count=6, around=16)
            for o in (body, core):
                k.smooth(o, 80)
            parts.append(Part(body, [("glow", 0x73, 0.32)] * len(body.data.polygons), (x, y)))
            parts.append(Part(core, [("glow", 0x78, 0.55)] * len(core.data.polygons), (x, y)))
    return parts


def fang(name, base, tip, radius, arch, segments=12, steps=10):
    """A curved cone from base (x, y, z) to tip, its middle raised by arch, radius at its base (sunk into the lip)."""
    b, t = Vector(base), Vector(tip)
    mid = (b + t) / 2 + Vector((0.0, 0.0, arch))
    rings = []
    for i in range(steps):
        u = i / steps
        p = (1 - u) ** 2 * b + 2 * u * (1 - u) * mid + u * u * t
        d = (2 * (1 - u) * (mid - b) + 2 * u * (t - mid)).normalized()
        side = d.cross(Vector((0.0, 0.0, 1.0)))
        if side.length < 1e-6:
            side = Vector((1.0, 0.0, 0.0))
        side.normalize()
        up = side.cross(d).normalized()
        rad = radius * (1.0 - u) ** 0.62 + 0.08
        rings.append([p + side * (rad * math.cos(2 * math.pi * j / segments)) +
                      up * (rad * 0.85 * math.sin(2 * math.pi * j / segments)) for j in range(segments)])
    obj = k.loft(name, rings, None, cap_start=True, cap_end=True, start_point=b - (mid - b).normalized() * 0.3,
                 end_point=t)
    k.smooth(obj, 70)
    return obj


def tooth_keys(obj, base, tip):
    """A fang's faces: bone by how the game's sun lights them, darker at its foot, paler at its tip."""
    centres, normals = gw.face_data(obj)
    lit = gw.sun_on(normals)
    b, t = np.array(base), np.array(tip)
    axis = t - b
    u = np.clip(((centres - b) @ axis) / max(1e-9, axis @ axis), 0.0, 1.0)
    s = 4.0 + 7.5 * lit + 2.0 * u - 2.5 * (1.0 - smoothstep(0.0, 0.25, u))
    return [("bone", int(v)) for v in gw.nearest(s, INKS["bone"][1])]


def teeth_parts(beast, fold=1.0, broken=None):
    """The fangs; fold: the top lip's two long fangs this much of their length (the frames fold them back); broken:
    {tooth name: how much of it is left}."""
    specs = []
    for i, spec in enumerate(TEETH):
        specs.append(("tooth%d" % i, spec))
        (bc, br), (tc, tr), rad, droop, arch = spec
        specs.append(("tooth%d_m" % i, ((2 * AXC - bc, br), (2 * AXC - tc, tr), rad, droop, arch)))
    specs.append(("tooth_axis", TOOTH_AXIS))
    parts = []
    for name, ((bc, br), (tc, tr), rad, droop, arch) in specs:
        bx, by, tx, ty = X(bc), Y(br), X(tc), Y(tr)
        zb = surface(beast, bx, by) - 0.2
        zt = max(surface(beast, tx, ty) + 1.0, zb - droop)
        base, tip = Vector((bx, by, zb)), Vector((tx, ty, zt))
        keep = 1.0
        if name in ("tooth0", "tooth0_m"):
            keep = fold
        if broken and name in broken:
            keep = min(keep, broken[name])
        if keep < 1.0:
            tip = base + (tip - base) * keep
        obj = fang(name, base, tip, rad, arch * keep)
        parts.append(Part(obj, tooth_keys(obj, base, tip), (bx, by)))
    return parts


# --- Building --------------------------------------------------------------------------------------------------------

def boss_check(beast):
    """The beast's outline as the camera sees it (the sheared heightfield puts each point where the sprite draws it:
    its cells) against the sprites' pixels, the whole and each piece."""
    ip = beast.intact
    covered = gw.own_coverage(lambda Xa, Ya: beast.shape.inside(Xa, Ya), ip.w, ip.h, ip.left, ip.top)
    mask = (ip.a >= 0).tolist()
    mk.compare("the boss (its 120 x 168 picture)", covered, mask)
    for sprite, (c0, r0) in CELLS.items():
        sub_c = [row[c0:c0 + 24] for row in covered[r0:r0 + 28]]
        sub_m = [row[c0:c0 + 24] for row in mask[r0:r0 + 28]]
        both = sum(a and b for ra, rb in zip(sub_c, sub_m) for a, b in zip(ra, rb))
        either = sum(a or b for ra, rb in zip(sub_c, sub_m) for a, b in zip(ra, rb))
        print("silhouette overlap gyges_maw_%d (n %d): %.3f" % (sprite, sprite, both / max(1, either)))


def build_look(look, options, only, out, check=None):
    """The boss of one look ('intact', 'damaged' or a frame), its pieces exported."""
    intact_pic = Pic(boss_rows("intact"), LEFT, TOP)
    pic = Pic(boss_rows(look), LEFT, TOP) if look != "intact" else intact_pic
    beast = Beast(pic, intact_pic, wounded=look == "damaged")
    plate = gw.Plate((-60.0, 60.0, -84.0, 84.0), beast.heights, cells=beast.cells)
    paint = Paint(beast)
    fold = FRAMES[look][1] if look in FRAMES else 1.0
    lit = (lambda i, side: (i, side) == LIT_WHEN_DAMAGED) if look == "damaged" else None
    broken = BROKEN if look == "damaged" else None
    if check and look == "intact" and only is None:
        boss_check(beast)
    if look == "intact":
        pieces = [(s, "gyges_maw_%d" % s) for s in CELLS]
    elif look == "damaged":
        pieces = [(s, "gyges_maw_%d" % DAMAGED_OF[s]) for s in CELLS if s in DAMAGED_OF]
    else:
        pieces = [(s, "gyges_maw_%d" % f) for s, f in zip(MIDDLE, FRAMES[look][0])]
    for sprite, model in pieces:
        if only is not None and model not in only:
            continue
        k.reset()
        box = box_of(sprite)
        owns = gw.piece_owner(box)
        mesh_obj, kinds, wall_z = plate.mesh(model, owns)
        parts = []
        if mesh_obj is not None:
            parts.append((mesh_obj, plate_keys(mesh_obj, kinds, paint)))
        extra = fire_parts(beast, FRAMES[look][2], FRAMES[look][3]) if look in FRAMES else []
        for part in eye_parts(beast, lit) + teeth_parts(beast, fold, broken) + extra:
            if owns(np.array([part.anchor[0]]), np.array([part.anchor[1]]))[0]:
                parts.append((part.obj, part.keys))
            else:
                bpy.data.objects.remove(part.obj)
        assign(parts)
        gw.finish_piece(model, [p[0] for p in parts], box, out, options)


# --- The pincers -----------------------------------------------------------------------------------------------------
# The left pincer's picture (24 x 56: n 163 above 201): column c is x = c + 0.5 - 12, row r is y = 27.5 - r.

def PX(c):
    return c + 0.5 - 12.0


def PY(r):
    return 27.5 - r


# Its shell, the hand and the big finger: per row of the picture, the left and right edge (columns, the pixels' outer
# edges) and the height of its top; a seam between the hand and the finger at row 15.
SHELL = [(0.4, 5.0, 6.6, 1.8), (1.0, 4.6, 7.6, 3.0), (2.0, 4.5, 8.8, 4.2), (3.0, 4.4, 10.8, 5.0),
         (4.5, 4.2, 12.4, 5.8), (6.5, 3.5, 13.4, 6.2), (8.5, 2.6, 13.4, 6.3), (10.5, 2.4, 12.8, 6.2),
         (12.5, 2.4, 12.2, 6.0), (14.2, 2.0, 12.0, 5.6), (15.0, 1.3, 11.8, 4.6), (15.8, 0.6, 11.8, 5.2),
         (17.5, 0.5, 11.6, 5.4), (19.5, 0.5, 11.2, 5.1), (21.5, 0.8, 10.6, 4.6), (23.5, 1.6, 9.4, 3.9),
         (25.5, 2.4, 9.0, 3.3), (27.5, 3.5, 9.0, 2.7), (29.5, 4.5, 9.3, 2.1), (31.0, 6.0, 10.0, 1.5),
         (32.2, 7.3, 10.7, 1.0), (33.2, 8.6, 11.3, 0.6)]
SHELL_TIP = (10.4, 33.9, 0.3)
SHELL_POWER = 2.6                 # its sections: superellipses, rounded boxes
# Per frame (the top sprite's): the ball joint's middle (column, row), its radius and height; the small finger's
# middle line from the joint down to its tip curling in (column, row, radius, height).
PINCER_FRAMES = {
    163: ((12.6, 13.6), 2.1, 4.4, [(12.9, 15.0, 1.9, 3.8), (13.5, 18.0, 2.0, 3.4), (13.7, 21.0, 2.1, 3.0),
                                    (14.6, 23.6, 1.9, 2.6), (15.8, 25.6, 1.5, 2.2), (15.9, 27.8, 1.2, 1.8),
                                    (15.0, 29.7, 0.9, 1.4), (13.9, 31.0, 0.5, 1.1)], None),
    203: ((15.2, 10.9), 2.1, 4.6, [(15.9, 12.6, 1.9, 4.0), (16.9, 15.6, 2.0, 3.5), (17.1, 18.4, 2.1, 3.1),
                                    (18.1, 20.6, 1.9, 2.7), (19.1, 22.8, 1.5, 2.3), (18.8, 25.2, 1.2, 1.9),
                                    (17.7, 27.0, 0.9, 1.5), (16.7, 28.4, 0.5, 1.2)], [(11.0, 11.5, 1.5, 4.6),
                                                                                    (13.6, 10.8, 1.3, 4.6)]),
    207: ((17.6, 8.9), 2.1, 4.8, [(18.5, 10.6, 1.9, 4.2), (19.3, 13.6, 2.0, 3.7), (19.7, 16.4, 2.1, 3.3),
                                   (20.7, 18.8, 1.9, 2.9), (21.3, 21.2, 1.5, 2.5), (20.9, 23.6, 1.2, 2.1),
                                   (19.7, 25.4, 0.9, 1.7), (18.7, 26.6, 0.5, 1.4)], [(11.0, 10.4, 1.6, 4.8),
                                                                                   (13.4, 9.6, 1.4, 4.8),
                                                                                   (15.6, 9.0, 1.2, 4.8)]),
}
# The models: (top sprite, bottom sprite) of the left pincer and of the right one, for each frame.
PINCER_MODELS = {163: ((163, 201), (11, 49)), 203: ((203, 205), (9, 47)), 207: ((207, 245), (1, 39))}
PINCER_SHADES = [0x61, 0x63, 0x65, 0x67, 0x69, 0x6b]
PINCER_FINISH = (0.35, 0.24)
SUN3 = np.array([-0.6, 0.6, 1.0]) / np.linalg.norm([-0.6, 0.6, 1.0])


def pincer_shell():
    rings = []
    for r, left, right, top in SHELL:
        cx, hw = PX((left + right) / 2.0 - 0.5), (right - left) / 2.0
        rings.append(k.ring(PY(r), hw, top / 2.0, 28, z=top / 2.0, x=cx, power=SHELL_POWER))
    first = rings[0]
    start = sum(first, Vector()) / len(first) + Vector((0.0, 0.4, 0.0))
    tx, ty, tz = SHELL_TIP
    obj = k.loft("pincer_shell", rings, None, start_point=start, end_point=(PX(tx), PY(ty), tz))
    k.smooth(obj, 50)
    return obj


def pincer_finger(points):
    path = [Vector((PX(c), PY(r), z)) for c, r, _, z in points]
    radii = [rad for _, _, rad, _ in points]
    rings = []
    for i, p in enumerate(path):
        a, b = path[max(i - 1, 0)], path[min(i + 1, len(path) - 1)]
        d = (b - a).normalized()
        side = d.cross(Vector((0.0, 0.0, 1.0))).normalized()
        up = side.cross(d).normalized()
        rings.append([p + side * (radii[i] * math.cos(2 * math.pi * j / 16)) +
                      up * (radii[i] * 0.9 * math.sin(2 * math.pi * j / 16)) for j in range(16)])
    tip = path[-1] + (path[-1] - path[-2]).normalized() * 0.5
    obj = k.loft("pincer_finger", rings, None, start_point=path[0], end_point=tip)
    k.smooth(obj, 60)
    return obj


def shade_keys(obj, shades, base, spread, under=None):
    """Faces painted by how the game's sun lights them (base + spread * lit shades), the underside `under`."""
    centres, normals = gw.face_data(obj)
    lit = np.clip(normals @ SUN3, 0.0, 1.0)
    s = base + spread * lit
    keys = [("pincer", int(v)) for v in gw.nearest(s, shades)]
    if under is not None:
        keys = [under if normals[i, 2] < -0.3 else key for i, key in enumerate(keys)]
    return keys


def pincer_mat(key):
    kind, index = key[0], key[1]
    if kind == "pincer":
        return pal("pincer", index, *PINCER_FINISH)
    if kind == "knob":
        return pal("pincer_knob", index, 0.2, 0.12, key[2])
    return pal("pincer", DARK, 0.2, 0.4)


def build_pincers(options, only, out, check=None):
    for frame, ((lt, lb), (rt, rb)) in PINCER_MODELS.items():
        knob_at, knob_r, knob_z, finger, bridge = PINCER_FRAMES[frame]
        for right, (top, bottom) in ((False, (lt, lb)), (True, (rt, rb))):
            names = ["gyges_pincer_%d" % top, "gyges_pincer_%d" % bottom]
            if only is not None and not set(names) & only:
                continue
            k.reset()
            shell = pincer_shell()
            fing = pincer_finger(finger)
            kx, ky = PX(knob_at[0]), PY(knob_at[1])
            knob = gw.ellipsoid("pincer_knob", (kx, ky, knob_z), (knob_r, knob_r * 0.95, knob_r * 0.85), None,
                                count=10, around=24)
            k.smooth(knob, 80)
            objs = [shell, fing, knob]
            arm = pincer_finger(bridge + [(knob_at[0], knob_at[1], 1.0, knob_z)]) if bridge else None
            if arm is not None:      # the knuckle the opened joint hangs from
                objs.append(arm)
            if right:        # the right pincer: the left one mirrored about x = -0.5 (its picture's column 11)
                for o in objs:
                    o.data.transform(Matrix.Translation((-0.5, 0, 0)) @ Matrix.Scale(-1, 4, (1, 0, 0)) @
                                     Matrix.Translation((0.5, 0, 0)))
                    o.data.flip_normals()
                    o.data.update()
            # Painted after mirroring: lit from the game's sun at the upper left on both.
            parts = [(shell, shade_keys(shell, PINCER_SHADES, 1.6, 8.5, ("dark", 0))),
                     (fing, shade_keys(fing, PINCER_SHADES, 1.6, 8.5, ("dark", 0)))]
            if arm is not None:
                parts.append((arm, shade_keys(arm, PINCER_SHADES, 1.2, 7.0, ("dark", 0))))
            centres, normals = gw.face_data(knob)
            lit = np.clip(normals @ SUN3, 0.0, 1.0)
            knob_keys = [("knob", 0x3c, 0.45) if lv > 0.93 else ("knob", 0x3a, 0.3) if lv > 0.72 else
                         ("knob", 0x37, 0.2) if lv > 0.35 else ("knob", 0x35, 0.14) for lv in lit]
            parts.append((knob, knob_keys))
            order = sorted({key for _, keys in parts for key in keys}, key=str)
            mats = [pincer_mat(key) for key in order]
            for obj, keys in parts:
                obj.data.materials.clear()
                for m in mats:
                    obj.data.materials.append(m)
                obj.data.polygons.foreach_set("material_index", [order.index(key) for key in keys])
                obj.data.update()
            dark = pincer_mat(("dark", 0))
            for name, box in ((names[0], (-12.0, 12.0, 0.0, 28.0)), (names[1], (-12.0, 12.0, -28.0, 0.0))):
                if only is not None and name not in only:
                    continue
                pieces = [p for p in (cut(o, box, dark) for o in objs) if p is not None]
                mk.transform(pieces, Matrix.Translation((0.0, -(box[2] + box[3]) / 2, 0.0)))
                bpy.context.view_layer.update()
                triangulate(pieces)
                piece = join(pieces, name) if len(pieces) > 1 else pieces[0]
                piece.name = name
                drop_unused([piece])
                bpy.context.scene.view_settings.view_transform = "Standard"
                if check:
                    sprite = top if box[2] >= 0 else bottom
                    mk.compare("%s (n %d)" % (name, sprite), mk.coverage([piece], 24, 28), k.sprite_mask(check, sprite))
                mk.report(name, [piece], os.path.join(out, name + ".glb"))
                if "preview" in options:
                    mk.preview(options["preview"] + name, [piece])
                bpy.data.objects.remove(piece)


def build():
    options = k.args()
    out = mk.outdir(options)
    only = set(options["only"].split(",")) if "only" in options else None
    check = None
    if "check" in options:
        sheets = options["check"]
        check = os.path.join(sheets, "enemy_N.png") if os.path.isdir(sheets) else sheets
    groups = {"boss": ["intact"], "open": list(FRAMES), "damaged": ["damaged"], "pincers": ["pincers"]}
    looks = ["intact"] + list(FRAMES) + ["damaged", "pincers"]
    if only is not None and only & set(groups):
        looks = [lk for g in sorted(only & set(groups)) for lk in groups[g]]
        only = None
    for look in looks:
        if look == "pincers":
            build_pincers(options, only, out, check)
        else:
            build_look(look, options, only, out, check)


# --- The sprites' pixels ----------------------------------------------------------------------------------------------
# Each pixel its palette index as two hex digits ('..' none), rows top to bottom. BOSS: the 120 x 168 picture the events
# lay out (its rows 0-151; the rest are empty); DAMAGED and OPEN_<frame>: the runs of pixels ('row:column:hex') where
# the damaged sprites and the maw's frames differ from it; CLAW_<sprite>: the left pincer (its top sprite above its
# bottom one, 24 x 56) in the first frame and its two opening frames.

BOSS = """
................................................................................................................................................................................................................................................
................................................................................................................................................................................................................................................
................................................................................................................010101010101......010101010101..................................................................................................
..........................................................................................................010101016162636101010101016163626101010101............................................................................................
......................................................................................................01010160616161656865626101616265686561616160010101........................................................................................
....................................................................................................010101016060616163666362600160626366636161606001010101......................................................................................
..................................................................................................0101010101606061616164626260016062626461616160600101010101....................................................................................
................................................................................................01010101010101606060616161610101016161616160606001010101010101..................................................................................
..............................................................................................010101010101010101606060606001016001016060606060010101010101010101................................................................................
............................................................................................010101010101010101010101010101......0101......010101010101010101010101..............................................................................
......................................................................................0101016161616160010101010101606161010101010101010101500101010101016061616161010101........................................................................
................................................................................0101016061616162626261616160010161616101010101510101010101010101016061616162626261616160010101..................................................................
............................................................................010160616161626262626262626262616161606262515151515151515151515150616161626262626262626262616161600101..............................................................
..........................................................................0101016161626262626363636363636363626261626352525252525252525252510162626363636363636363626262626161010101............................................................
................................................0101....................60606161626262636363636363636363636364646261635252525252525252525201626464636363636363636363636362626261616060..........................................................
................................................606001................010160616263636363636363636363636363636465636162525252525252525252516163656463636363636363636363636363636261600101........................................................
................................................616001..............0101016161616161616161616262636363646464646567636264535353535353535362636765646464646363636262616161616161616161010101......................................................
................................................616001............010160606061620101010101616162626464646465656568656265655454535454545462656865656564646464626261610101......51016060600101....................................................
................................................616001..........01610160600101....515151610161616263646464656565696b6365675757535857575463696a656565646464636261610161515151........6060016101..................................................
................................................6001010101010101010101010101..5151515557546101606162636464646565676b656668595b585d595855656a696565646464636261600161545454515151......0101010101................................................
................................................60010101626463606163610101505151515152595c55600161626363646465656569666568595b595d595854666a6865656464636362610160545955525151515150..0161636160................................................
................................................01010163646565616263626101..5151515151015455510101616263636464656566656468595a575b595853656766656464636362610101515453015151515151....6162636261................................................
................................................01016063636664626365646260..5151510101015153520101616263636464656565646466575755575755536466656564646363626101..525351010101515151..506264656362................................................
................................................0101016363646262626362626101505101010101010152500160626363636464656563656554545454545454636565646463636362600150520101010101015150..616262636262................................................
................................................610101616261626364626161600160..0150500150500101010161636363646464636265535353535353535462636464646363636101010101505001505001..5001606161626463................................................
................................................62010162636263646460010101016060............0150600160636363636363636363525252525252525263636363636363636001606001............506001010101606464................................................
................................................610101636462636361616001616161616150505050500150010160016161636363636364545557575755545363636363636161016001016061505050505001616161610160616163................................................
................................................010163636362626160610161616161616160505050015101010101016164646668595a55585a5a5b5a5a58556a696866646461010101010162616060606061616161616101616061................................................
................................................626362636363636161016162626262616161605050..016161616365685857595b5c5b57595b5c5c5c5b59575b5c6b69676868656361616101016060606161616262626261016161................................................
................................................63636464646464626060626262636261616001010101626162646667595b555758585957585959595959585759585857666b69676664626162010101016061616263626262606062................................................
................................................636464646464646260616263636363626060010161606364686464575858575757595b5557575757575757555b595757575858676464656363606101016060626363636362616062................................................
................................................646464646464646361626565646463626101016163616366696465545454545457585954555555555555555459585754545454545453676563616361010161626364646565626163................................................
................................................646465656565656462636665656463626001626367646253545253525254545455575753545555555555545355555554545452525352545362646763620160626364656566636264................................................
................................................646565656565656561646665656564626001636364645152535759545254585554555554535455555554535455555455555452535554535251646463630160626465656566646165................................................
................................................6565656566666665626667666565646260016263625251535353525153555b5854555454545454545454545454555457555453515253535351526263620160626465656667666265................................................
................................................656566666666666562666766656463610101616151535151525253535455585754545455585a57555758555554545455555554535352525151535161610101616364656667666265................................................
................................................656666666666666561656866656464610161636051575351535452535355555554545455555757555757555554545455555553535253535153575160636101616464656668656165................................................
................................................656666666666666563626768656464610161656151545452555a52545355545457585454555555555555555454555554545453545257545254545161656101616464656867626365................................................
................................................67666666666666656460646666646260016163615152535253555253555c5954555a5754555555555555555455575554575754535254535253525161636101606264666664606465................................................
................................................6b6766666666656564620161636361010161606101515252535352515457555455555555545555555555545555555554555454515253535252510161606101016163636101626465................................................
................................................6e6a67666665656463636101010101010101016151525151525252525457545455555554545455555554545455665554545454525252525151526261010101010101010161636364................................................
................................................6a6c69666564646361616160626161616001016163520151015053545255545354555353535353545353535353556553545452545350015101636361010160616161626061616163................................................
................................................656868676664636001016262626262616160016061610151530152535252015252535352535557585755535253535252515252535201535161616160016061616262626262010160................................................
................................................6565656563606060016163636261626261610101606061515101525250....5358595957595a5d5c5d5a595759595853....50525201626261606001016161626261626363610160................................................
................................................616363646101616061646463646463636261610101606060505001....525455585a5c5b595a5b595b5a595b5c5a58555452....6160606060600101616162636364646364646160................................................
................................................606001606301010163646464646464646362626001010101......0154555455555a5a5958575858585758595a5a5555545565620101010101010160626263646464646464646301................................................
................................................010101616601626365656565656564646464636261010101....505452555b5a53585858545757555757545858585358595563656001010101016162636464646465656565656563................................................
................................................016060606160626565656565656565656464636362616050..5051555255585752535453555955555559555354535257585552666260016060616263636464656565656565656565................................................
................................................616262616101616665656565656565656564646362626150..0152535153535254545253535454555454535352535352535351646361016061626263646465656565656565656566................................................
................................................626263636461626766656565656565656565646363626150..51525152575253575b5452535354545453535253575453525452516362016061626363646565656565656565656666................................................
................................................636363646463626766666665656565656565646363626150..520101545c595255555452535454545454535254545452575554016163016061626363646565656565656566666666................................................
................................................636364646465626869676666666565656565646363626150..0101505157545253545254535354545453535352545352545451506161016061626363646565656565666666676767................................................
................................................63636464656562686b676666666665656565646363626150..015257015051515253555a555353545353545453525251515001576361016061626363646565656566666666676867................................................
................................................63646464666662666c6a6766666666656565646363626150..5152545201535954515458545353535353545554015358530152546362016061626363646565656666666667686966................................................
................................................6364646567666464686d6866666666666565646363626160....525251525252525153535252525352525253535152525252515263010160616263636465656666666666676a6864................................................
................................................636464666968656264696d68666666666565646363626161......52515201015053535153545455545453515353500101525152010101616162636364656566666666686a686462................................................
6264656401........01015150..5163600160616262626263646466686b69656465686a6a66666665656463636261610150........525252535354595b5b5b5b5b59545353525252......01600161616263636465656666666767676564656869686664646362626262616001606351..5051..01....
01010101............0101....6101010101606262626263646466676a6c66666465656767666665656463626261606001..51515252525354585a5b5a5a5a5a5a5b5a585453525252515101016060616262636465656666676765656465666a68676664646362626262600101010161......01......
..........................01010101010160626262626364646566676b6d6765646364656666656564626260600101626201015555575555575b5a5a5958595a5a5b5755555755550101626201016060626264656566666564636465666a696766656464636262626260010101010101............
..........................0160600101016062626262636364646565666969686664656565656464646262610101616565645255555a575357595c5a5857585a5c595753575a555552536565610101616262646464656565656466686968666565646463636262626260010101606001............
..........................016162600101016062626263636364646465656566666666676765626363636461016263656462535557575552535557595a595a59575553525557575553516465636201616463636362656767666666666565656464646363636262626001010160626101............
..........................0161626360016060616262626363636464646464646464646467666062626263646201626462515455575553575453535455545554535354575355575554516264620162646362626260666764646464646464646464636363626262616060016063626101............
..........................01616163646060016061626262626363636363636363636363656501010101016161600161615152535354545a59545557555555575554595a5454535352510161016061610101010101656563636363636363636363636262626261600160606463616101............
..........................0161616263646360600160616262626262626262626262626265620101010101616201016364525553015455575754575957555759575457575554515355525363010162610101010101626562626262626262626262626262616001606063646362616101............
..........................01616161616365656261616060606161616161616161616262616001010101016162010163655254585354575454575a5b5958595b5a5754545754535854525463010162610101010101606162626161616161616161616060606161626565636161616101............
..........................0161616161616364666563616060606060606060606001010101606201010160626101016464525457535254575555595855585558595555575452535754525364010161626001010162600101010160606060606060606060616365666463616161616101............
..........................0160616161616262626263636362626161616161616301010165656562626263626201636362535454535455575553535357595753535355575554535454535163630162626362626265656501010163616161616161626263636362626262616161616001............
..........................0101606161616161626161616161616161626262010163646565666664626263630161626163535352525554545453525455575554525354545455525253535261626101636362626466666565646301016262626161616161616161626161616161600101............
............................010101606160606060616161616262626262010164656565656666646062636301636564646252520101535353515153545454535151535353515152525153646563016363626064666665656565640101626262626261616161606060606160010101..............
..............................01010101010160606160010101010101010162626263646564636262656665630164656364520101505050010151525252525251010150505051015253526564016365666562626364656463626262010101010101010160616060010101010101................
................................0101016001010101010101016162646566656465656566656561636769666462646462676450515152510151525252525252525101515251515053576264646264666967636165656665656564656665646261010101010101010160010101..................
..............................60600101010160606001016164626666656462636464646566666266696862636461626161625051515152015152525252525252510152515151505101616261646362686966626666656464646362646566646264610101606060010101016060................
............................0160616161626261616001016462636b63616366666666666666676367686160016663616161600150010101015152525252525252510101010150..506161616366016061686763676666666666666663616266626264010160616162626161616001..............
............................016161626365656261016001636268666166686765646364636465646564010101666301616001606001010150015152535353525101500101015050016061016366010101646564656463646364656767656163666263016001616265656362616101..............
............................01616161616162616001600160636462666d686263636366686b68666563010101676763010101016162545250015252535353525201505254510101010101636767010101636566686b68666363636266696562646360016001606162616161616101..............
............................0161616162626160010101010163626169686361646566686b6f6b6866646260616866636261606062636251505152525454545252515051515262606061626366686160626466686b6f6b686665646163666661626301010101016061626261616101..............
............................010160616160600160010101016461646664626266666666666768696766676668686461010101010165646360515254545454545251505264650101010101616468686667666769686766666666666262646664616401010101600160606161600101..............
..............................0101010101010101016001606261646362606566666261616264676764666b69656201010101010166656061636466656565666463616065660101010101016265696b666467676462616162666665606263646162600160010101010101010101................
................................0101010160626260600162616164636062666361636261616163686265666466620101010101016763016365676766666667676563016367010101010101626664666562686361616162636163666260636461616201606062626001010101..................
..................................010161626201016001616061646260646360017072720101626761626365676401010101016266636066686969686668696968666063666201010101016467656362616762010172727001606364606264616061016001016262610101....................
................................01016061626061656061600160636262646101707478787201636663626465676866646262626360606467696a6a6967696a6a6967646060636262626466686765646263666301727878747001616462626360016061606561606261600101..................
............................01016161606162616762016461010160616263620170747a797001636563626465656768666665626162656666696b6c6b696b6c6b696666656261626566666867656564626365630170797a7470016263626160010161640162676162616061610101..............
............................016060616062636961016663606101016062646360707072717001636463666563656566686864636563646567686a6b6a676a6b6a68676564636563646868666565636566636463017071727070606364626001016160636601616763626061606001..............
..........................01016061600162646d616864606465616201656565635001707001636363636b68646467696d686362636262646565666768666867666565646262636263686c69676464686b63636363017070015063656565016261656460646761666462016061600101............
..........................016001600160636469606b626768626265686d6b666501010264646466676467676465686768676263666463636463646463626364646364636364666362676867686564676764676664646402010165666b6d676562626664626760656463600160016001............
..........................0161606001606362676168606c666265666966646564636364666662666661626363656563666262686a66636162656765016301656765626163666a6862626663656563636261666662666664636364656466686565626467606561656263600160606101............
........................01016162640160636167016561686163646460707170016462656766606464616266646162606363646466656161646669666063606669666461616566646463636062616466626164646066676562640170717060646463616761650166616360016462610101..........
......................016061616163016063616460656266616364017074777570016264636361616163656664626161696865626364606264666663606260636666646260646362656869616162646665636161616363646201707577747001646361666265606461636001636161616001........
....................016160606161600160626163606262656263640171767d78710163616664626163646464626264666d6a6462686c6865626461616161616161646265686c6862646a6d66646262646464636162646661630171787d76710164636265626260636162600160616160606101......
..................01016161606001010161626063606361646164646470737874700165616301606263646463016567686765656364666666656401606463646001646566666664636565676867650163646463626001636165017074787370646464616461636063606261010101606061610101....
..................01616161606001016061626061616160636162636301717171016465606061636361636262016667676563600160616261610161646563656461016161626160016063656767660162626361636361606065640171717101636362616360616161606261600101606061616101....
..................01616160016061616060626261616001606163626161016161646461616264646461626364016466646361014143454546464645444444444445464646454543410161636466640164636261646464626161646461610161616263616001606161626260606161600160616101....
..................01616001016161636301626261600161626467666464646464626060606365646463646765626162630101414345464848484846424343434246484848484645434101016362616265676463646465636060606264646464646667646261016061626201636361610101606101....
..................0101010160016161630162616062606364676461606161616161616062636463636465676862606101014042444545494a4d4946424445444246494d4a494545444240010161606268676564636364636260616161616161606164676463606260616201636161016001010101....
..................010160616101606160016260616401616563600101700161616162016163636263656565630160011010414244454548494b4844434446444344484b49484545444241101001600163656565636263636101626161610170010160636561016461606201606160016161600101....
..................0161636162010160016062606162016263600101747571016162626201616061656464636061a041424241424344444444444444444548454444444444444444434241424241a06160636464656160610162626261017175740101606362016261606260016001016261636101....
..................0162646163600101010160016060016160600174797a7501626263620161616063636262014041434445444242424201a14141424346484643424141a101424242424445444341400162626363606161016263626201757a797401606061016060016001010101606361646201....
................01626661616361016060010101606101606060017177797341626362616164666260636160404141444648444341a0a4a8a9a3a242414747474142a2a3a9a8a4a041434448464441414060616360626664616162636241737977710160606001616001010160600161636161666201..
................6167620161646101606262600101610160616161017173710164646061626667656060a0414242434446464442a0a4a7ababa7a401434849484301a4a7ababa7a4a0424446464443424241a06060656766626160646401717371016161616001610101606262600161646101626761..
..............01656901..016560606062636001616360606060616101400162626260626464636361604345454443424442400101a6a8ababa7a401414445444101a4a7ababa8a6010140424442434445454360616363646462606262620140016161606060606361016063626060606501..01696501
..............01636201..0166606060606060016365600101606061626264646161606264630101014246494a4643400101a00101a4a6acaba643..0141414101..43a6abaca6a40101a001014043464a494642010101636462606161646462626160600101606563016060606060606601..01626301
................6001....01680101010101010166606262016161626466656262616061630101014244494d4a44a201a1a0a3a10141a4aaaba742..01a2a3a201..42a7abaaa44101a1a3a0a101a2444a4d4944420101016361606162626566646261610162626066010101010101016801....0160..
......................0163660101010101016367016166606061646a65626162626001404140404144494a46a4a5a5a2a0a3a40101a0a7aba84101a1a3a6a3a10141a8aba7a00101a4a3a0a2a5a5a4464a49444140404140016062626162656a646160606661016763010101010101666301........
....................0163646501....0163616861606262616060616362616262606041424241410142444413a6aaa6a30141a4010101a4a8a8400101a3a4a3010140a8a8a4010101a44101a3a6aaa61344444201414142424160606262616263616060616262606168616301....0165646301......
....................0165656301....60636664010161616161636061616162610141414344444343014242a4a8abaaa8a30141a00101a0a6a8010101a1a4a1010101a8a6a00101a04101a3a8aaaba8a442420143434444434141016162616161606361616161010164666360....0163656501......
..................01626c6601....01016664010101010162636563600160606001414143444547494341a0a5a6a7adaba6010170010101a4a801010101a201010101a8a4010101700101a6abada7a6a5a041434947454443414101606060016063656362010101010164660101....01666c6201....
..................01646b6301....01646401........01016569656160616001014241414344474846a1a2a0a3a5a6aaaaa70170010101a1a601010101a001010101a6a10101017001a7aaaaa6a5a3a0a2a146484744434141420101606160616569650101........01646401....01636b6401....
..................01656761....01636401..........ff01636b6360016161600143434343434545a1a3a5a101a0a1a2a2a3a17001010101a4010101010101010101a40101010170a1a3a2a2a1a001a1a5a3a145454343434343016061610160636b6301............01646301....61676501....
..................01616101....016501............ff01656a61016061616201444545454444a0a1a2a2a3a1010101010101700101010170010140404040400101700101010170010101010101a1a3a2a2a1a0444445454544016261616001616a6501..............016501....01616101....
....................0101......016601............01646762016161616062614444464745a3a3a5a401a0a1a001017001017001010101707001010101010101707001010101700101700101a0a1a001a4a5a3a345474644446162606161610162676401............016601......0101......
............................01616860..........6065676101636362626263610142464a45a5a8aaa9a6010101a00170010170700101010170707001010170707001010101707001017001a0010101a6a9aaa8a5454a464201616362626263630161676560..........60686101..............
............................01626b6701......606166616362636363616365626101434644a6a6a9abaaa7a2010101700101707001700101010170707070700101010170017070010170010101a2a7aaaba9a6a6444643016162656361636363626361666160......01676b6201..............
............................0162696501....01646601010162636362626267646561424443a3a2a3a6a8aaa9a5a20170010170700170700101010101700101010101707001707001017001a2a5a9aaa8a6a3a2a343444261656467626262636362010101666401....0165696201..............
............................0161636201....616501......01626262626265656560604443404001a0a2a4a5a6a5a2707001707170017070700101010101010170707001707170017070a2a5a6a5a4a2a001404043446060656565626262626201......016561....0162636101..............
..............................010101....016601........01010164636064626365600141010101010101010101017170010171700101717070700101017070707101017071010170710101010101010101010141016065636264606364010101........016601....010101................
........................................016801............01016461626265666101014040a0a1a1a1a1a101017170010170717001017171707001707071710101707170010170710101a1a1a1a1a1a040400101616665626261640101............016801..........................
......................................60606601..............0163636263676861014042424241a0a3a3a3a10170717001017071700101707171717171700101707170010170717001a1a3a3a3a04142424240016168676362636301..............01666060........................
......................................01626601..............01636562646768640143454545464644434001404172700170707071700101017070700101017071707070017072414001404344464645454543016468676462656301..............01666201........................
......................................01626501..............016466626467676601434445494a4345a7a5a30101717270017070717170700101010101707071717070017072710101a3a5a745434a49454443016667676462666401..............01656201........................
......................................0162666701............016566636366676661014344484c45a9abacaaa6a401707271010170717171717070707171717170010171727001a4a6aaacaba9454c48444301616667666363666501............0167666201........................
......................................0161686d6501........01016667545155676766610142464742a8a9a9a6a2a001017073710101017171717272727171710101017173700101a0a2a6a9a9a842474642016166676766626567660101........01656d686101........................
......................................016167696401........01626658555150546665646101404241a6a3a2a00171700101727371010101707171717171700101017173720101707101a0a2a3a641424001616465666560625558556201........016469676101........................
......................................016160616101........0163545a585401515465646361010140010101014070707101017173717001010101010101010170717371010171707040010101014001016163646565626154585a545201........016161606101........................
......................................0101616201........016164545b5d5853..5062616361636301414211a2a2707072710170727372717070707070707071727372700171727070a2a211424101636361636162600153585d5b54530101........0162610101........................
........................................010101........0161625454555b5b55535263626160636540424513a3a1017072737170017173737271727172717273737101707173727001a1a3134542406563606162636353555b5b555454510101........010101..........................
......................................................0162545455555558550150616161626564414545a0a00101a6a7a572717001707272727272727272727001707172a5a7a60101a0a04545416465626161615001555855555554545101........................................
......................................................0101545454545454520153546061636664644343a3a7aaadaaa4717372707070010101010101010101707070727371a4aaadaaa7a343436464666361606553015254545454545401..........................................
........................................................52545454545452015151536101656965634647a9acaba701017071737172737171710170017171717372717371700101a7abaca947466365696501616451510152545454545452..57......................................
........................................................5354545454525001015152600165676563494aa6a6a3010101010170717274737272727172727273747271700101010101a3a6a64a496365676501606362010150525454545453..........................................
......................................................5053545453015050....0161606063656664474aa1a20101010101010101707072727272717272727270700101010101010101a2a14a476466656360606161....5050015354545350........................................
..................................................01..0154545150......0101600101610163635242460101017070707070a1a070707070717171717170707070a0a17070707070010101464252636301610101600101......5051545401..01....................................
..................................................016251535150....606162626260606162606060024344444201010101a0a9a1707001a30170707001a3017070a1a9a0010101014244444302606060626160606262510150....505153515101....................................
..................................................01626301......606061626260616261636561620244474846434201a1a6aea0707001aaa0707070a0aa017070a0aea6a1014243464847440262616563616261606262015050......01526201....................................
....................................................016160010101606061616161636462636665645345474c494301a1a5a8aba07101a0aca2717171a2aca00171a0aba8a5a10143494c47455364656663626463616161616050......506101......................................
......................................................010101010161616161616263646163696765534546484544a2a3a6a6a5017101a3aba5717171a5aba3017101a5a6a6a3a2444548464553656769636164636261616161610101010101........................................
................................................................01616160626362646163676765534545454643a2a5a5a4a1017101a4aba6717171a6aba4017101a1a4a5a5a243464545455365676763616462636260616101..................................................
..................................................................010101636462626063656565024344434846a5a4a2a001010101a6a8a5717171a5a8a601010101a0a2a4a5464843444302656565636062626463010101....................................................
......................................................................0163646260016165656403a24343444b4d494742420101a3a6a7a4717171a4a7a6a30101424247494d4b444343a20364656561016062646301........................................................
......................................................................016464016060606364646566666241444a474543410101a3a5a6a1717171a1a6a5a30101414345474a44416266666564646360606001646401........................................................
......................................................................016463016101016263656668676665654445454101434045454201010101014245454043014145454465656667686665636201016101636401........................................................
......................................................................01636001016062616064676967676565434345434346484b4a464541414145464a4b4846434345434365656767696764606162600101606301........................................................
......................................................................016101600162636161646969686866666664636565454646464644434143444646464645656563646666666868696964616163620160016101........................................................
........................................................................010162620160016166696a6a696867646263646565656465656464636464656564656565646362646768696a6a69666101600162620101..........................................................
..........................................................................0161620101606064656564656563626163646465666667686a6b686b6a686766666564646361626365656465656460600101626101............................................................
..........................................................................01600101606062626161616161606262616364646666656666696b6966666566666464636162626061616161616262606001016001............................................................
............................................................................010101636101616063616163646363606365636464636262646864626263646463656360636364636161636061016163010101..............................................................
..............................................................................01016260010160016163646361616001010101010101010166010101010101010101606161636463610160010160620101................................................................
..................................................................................0101606062626062616063630101............0162696201............0101636360616260626260600101....................................................................
......................................................................................01010101010101010101................01686c6801................01010101010101010101........................................................................
..........................................................................................................................0165676501............................................................................................................
............................................................................................................................010101..............................................................................................................
................................................................................................................................................................................................................................................
"""

DAMAGED = """
28:53:5452515454500101010150525353545a5b
29:52:5455010101010101010101010151525456555453
30:28:63636361
30:51:525150010101010171717171700150535257545151515151
30:95:61
31:26:63616060606060
31:51:010101010101017070010170720151535154525001010101010101
31:95:60
32:25:6361010160616060
32:36:64
32:47:505101010101010101010171700101717550545201010101010101010101010101
32:94:6160
33:24:6264616062646360016265626364
33:46:0101015352010101010101727574710101750101010101017071727372700101010101
33:94:0170
34:24:6262616164646101016162626164
34:45:0101010101a001017101017074777672707075700101010101010101707172737271010101
34:94:0101
35:24:61626001010101010161636364
35:44:0101010101a1a2a0017301017072737170017276700101010101010101505150707172710150
35:94:0101
36:24:6262010101010101016367
36:44:0151a0a0a1a3a4a1017201017072700101707176757101010101010101010101017072717154
36:94:0101
37:24:636260010162010161
37:44:01a0a1a2a2a3a4a0707071017071707071717173777401010101010101010101707273707151
37:93:610101
38:24:636261016160600163
38:44:0101a0a0a0a2a2a0700172700170017172737375787871010101010101010101717171727150
38:93:016101
39:24:686162610101016163
39:45:010101a0a3a3a0710171720101707273737473727573010101010101017071707173737241
39:93:616201
40:24:6d68656360010162
40:44:010101015050a5a07170017270707173737575747371747001
40:70:0101017072717273737372
40:94:6201
41:27:6563016061
41:45:01
41:47:01
41:49:51a5a1727101707101707172717270700101010101
41:71:0101707374737242714162
41:94:6060
42:29:6361
42:47:0101
42:50:50a37272
42:55:017070700171707001010101017070714072727574724251
42:95:01
43:34:626261
43:47:0101
43:50:5150a3
43:55:01010170017070010101700101017072724071737241
43:78:6161
43:86:6001010101606101
43:95:01
44:32:60626001616362
44:48:0101
44:53:a2a0710101010101707070707301010101510101404140503030
44:84:600101010101010101010101
45:32:01010101706061
45:52:51a2a2a071010101707272747777700101010101015063
45:84:6101010101010101a0a0a1
46:30:01010101017072736063
46:50:0101a0a1a1a0717101017073757675777001010101015150
46:75:64
46:83:616001010101010101a0a0a3a3
47:28:60010101010101a1a0737061
47:49:0101010101a0707171700170737573747471010101010101..0164
47:83:6260a0a0a1a2a0a0010101a0a1
48:27:6001
48:30:010101a0a3a4a2a07001
48:50:0170700101017071700171757373727473710101010101..5063
48:83:6261a1a2a2a3a4a5a6a4a10101
49:26:620170707001a2a7a5a5a271700164
49:49:017071727101010171017072737270707170727271700101....61
49:84:62a0a0a0a1a4a7a7acada5a0
50:24:61017070717271a2a7aba8a201700101626463
50:49:01
50:52:737170017071717272727001010170737273727001....50
50:84:6201010101a1a1a3a5adaeab
51:24:717271707070a2a1a4a8a4a07070707001616162
51:51:70717270017072717171700101010170717575737001....
51:84:6361010101010101a0a3a7a9
52:24:7272727001a1a201a0a3a0707173737270016062
52:50:0150
52:53:7172707072707001010101010101717275737001..5051
52:85:620101010101010101a0a4
53:24:7172710101a101a0a2a0010171727372700161
53:49:01010101
53:54:727070727001010101010101010171
53:70:7370..505051
53:85:630101a0a0a1a101010101
54:24:0101010101a001a2a001010101707070600163
54:50:0101017072717172700101010101010101017074727040....50
54:86:62a0a1a3a4a6a7a5a2a0
55:24:01010101616001a00101630101016060616363
55:51:010170
55:56:73747001010101010101010170727141a0....50
55:86:6462a0a0a2a4a6a9aca8
56:17:70
56:20:71720170010101606364620101016364656264636464
56:49:01
56:54:707173757201010101010101017171717170405050
56:87:65600101a0a1a4a9aeaca101a1a2a2010101010101
57:16:707170
57:20:707001010101a001606366616362
57:35:64656565
57:51:01010101017274537001700101010172505072714151
57:86:6463610101010101a2a8a9a7a1a0a2a2a10101a00101
58:16:707270
58:20:0101010101a1a101606166696564
58:53:51515251515150017172707070735271505156
58:86:646261010101010101a1a5a5a5a2a0a0a001a0a5a001
59:16:71727001010101a0a0a2010101016165666665
59:52:515352575301700101017373727351727070515553
59:85:6361010101010101010101a1a6a5a5a101a00101a4a101
60:17:7471
60:20:01010101a2a2a3a501016061626465
60:55:56517001010101017101717272727272505153
60:85:6201010101a0a0a101010101a0a5a6a201a00101a1a1a0
61:18:7470010101a4a6a1a9a201010160616263
61:54:565270727001010101700101707071727373705052
61:85:61010101a0a1a3a5a4a1010101a1a5a3a1010101a0a0a0
62:19:71
62:21:01a0a8aba9a6a0010101606162
62:54:51517374720101010101017170707172747571010150
62:87:010101a0a3a7a7a7a4010101a2a3a301010101
62:107:01
63:19:610101a1a6a8a3a001010101016061
63:55:507476757101010170727472707070727471015050
63:87:0101010101a2a5a8a8a5010101a1a3a001
63:105:010161
64:19:636201a0a3a4a0707070010101
64:54:52517273767571717373747450500101717370525050
64:87:01010101010101a6a9a7a4010101a3a2a001016062
65:19:62616270a0a001707071710101
65:55:500173727676777777757370707071727270525151
65:87:01
65:92:010101a5a8a6a30101a0a1a101010160
66:20:610170010101010101707060
66:56:52517271737374737272727250527271015153
66:88:62
66:92:a00101a0a6a9a6a20101a1a0a0010101
67:21:61010101010101017061
67:57:5101727272727271707050515151525051
67:88:646101a0a4
67:94:0101a1a5a7a3a00101a001010101
68:23:60010101016061
68:58:5101707171505152
68:89:646101a3a3a00101a1a4a4a101010101010101
69:60:0101015051
69:90:620101a2a1a0
69:98:a1a3a2a001010101
70:92:62616160010101a1a1a0
71:94:636362010101a0
71:103:010101
72:97:61010101
72:103:01010160
73:97:61600101
73:102:01
73:104:010164
74:98:610101
74:102:01
74:104:0101
75:98:6161
75:105:01
77:60:63647274737001017001
78:61:6471737201017071
78:70:62
79:36:010101
79:62:637271707070600160
79:88:010101
80:35:0101010101
80:62:68636101717071010101
80:87:0101010101
81:35:0101010101
81:63:676563727172010160
81:87:0101010101
82:35:0101010101
82:62:69646463717474010101
82:87:0101010101
83:37:0101
83:62:656262010170710101016261
83:88:0101
84:49:66
84:62:60010101017071010101620161
84:80:63
85:44:61
85:47:64646165
85:63:01
85:65:0101707001016366646061
85:79:646062
86:31:010101
86:43:0160656301010162
86:63:6001016270700101
86:72:6562636261
86:79:010164
86:93:010101
87:30:0101010101
87:42:6001616461010101
87:52:64
87:64:0101606001010163
87:75:666860
87:79:600163
87:92:01010101
88:30:0101010101
88:42:010101600101016369666261
88:65:0101600162666b
88:76:6c
88:78:6361016163
88:92:01010101
89:30:0101010101
89:41:6001016060
89:47:62626001016062
89:67:6162646565
89:77:676662
89:81:6062
89:92:01010101
90:31:010101
90:41:6001010101
90:47:616061010101
90:68:606061
90:74:01
90:78:6563
90:81:01616160
90:93:010101
91:39:63626101010160
91:47:6062016001
91:75:0162
91:78:6560
91:81:6261600162
92:37:01616362610101620101010161
92:77:61
92:79:010164
92:83:6361636264
93:36:01606162616101016062010101
93:78:01
93:80:61
93:85:61606162
94:30:01
94:35:61
94:37:016161010101606060
94:47:01
94:79:01
94:82:64
94:85:61016062
95:29:010101
95:36:61
95:38:0101016001606101
95:80:0101626363640101
95:95:01
96:28:01010101
96:36:61
96:38:01010160600101
96:82:61
96:85:62
96:95:01
97:28:01010101
97:36:60016065
97:42:610101
97:68:a2a7a6a3
97:95:01
98:29:010101
98:37:606365
98:67:a3a4a6a6a3a3
98:95:01
99:37:63616062
99:67:a2a1a4a4a2a3
100:38:61
100:68:01a2a401a0
101:68:0101a001
102:68:01010101
103:68:010101
104:68:010101
105:68:0101
106:68:0101
107:68:a0
108:42:a0a001a1a0
108:68:01
109:41:a2a301
109:45:010101
109:81:01
109:83:01a0a0a2
110:41:a7a6a101
110:65:010101
110:82:01a0a3a3a2
111:41:a5a4a1010101
111:64:0101
111:80:0101a0a1a0a0a3
112:42:01010101010101
112:57:01
112:69:0101
112:78:01a0a1a001010101a0
113:43:01010101a0a1a1
113:57:010101
113:67:010101
113:77:01a0a101010101
114:56:70
114:58:01010101
114:65:01010101
115:45:010101
115:55:7272
115:59:01010101
115:66:7001
115:79:0101010101
116:45:a2a1a101
116:56:75
116:60:010170
116:68:7172
116:78:0101010101
117:57:0101
117:68:7273
118:46:a5a101
118:56:0101010101
118:66:0101
118:69:72
118:78:010101
119:45:a7a7a7a5a1a1
119:54:73
119:57:0101010172
119:64:0101010170
119:76:010101010101
120:45:a6a5a4a10101
120:54:7675
120:59:010175737370010101
120:69:70
120:76:010101010101
121:45:a4010101
121:54:717570
121:58:70
121:60:017572
121:64:010101
121:69:72
121:78:01010101
122:55:0101707270
122:61:7070
122:68:0176
123:53:01
123:55:010101737471
123:62:71
123:64:010101010174
124:53:7001
124:56:7001707270017070700101010101
125:54:01
125:56:7373
125:59:70010101017001010101
125:70:010171
126:53:010170
126:57:72
126:59:72
126:68:010101017170
127:53:010101
127:57:7101
127:61:01
127:63:01
127:66:0101010101700101
128:55:01700170017170010171
128:67:7271010101
129:58:0171
129:61:717170
129:69:01
130:55:01010101
130:60:01
131:54:01a00101017001
131:66:01
132:53:a001a501
132:60:0101
132:65:01a1
133:53:a6
133:55:a901
133:59:010101
133:65:01a001
134:54:a7a6a0
134:59:010101
134:65:010101
135:59:010101
135:65:010101
136:59:010101
136:65:010101
137:58:01010101
137:65:01010101
138:58:01010101
138:65:01a00101
"""

OPEN_229 = """
93:79:30
94:79:30
95:81:30
95:87:30
96:57:a0
96:69:a0
96:86:30
97:55:a3a7a8a2a1
97:67:a1a2a8a7a3
97:82:30
97:85:30
98:54:a3a6aaaaa6a3
98:67:a3a6aaaaa6a3
98:84:3030
99:54:a5a61baaa613
99:67:13a6aa1ba6a5
99:84:30
100:54:12a4aaaa
100:60:01
100:66:01
100:69:aaaaa4a3
100:85:646066
101:49:a0
101:51:a2a0
101:54:40a2a8aaa6
101:60:01
101:62:a1a2a1
101:66:01
101:68:a6aaa8a2
101:74:a0a2
101:77:a0
101:79:a1
101:86:616363
102:48:a4a1
102:51:a2a3
102:56:a5a9a710
102:61:a0a2a5a2a0
102:67:10a7a9a5
102:74:a3a2
102:77:a1a4
102:80:a6
103:49:a2
103:52:a3
103:56:a2a6a701
103:62:a2a3a2
103:67:01a7a6a2
103:74:a3
103:77:a2
103:79:a9a8
103:85:62
104:48:1aa6a1
104:57:a4a7
104:62:a0a3a0
104:68:a7a4
104:76:a1a61a
104:80:a7
104:84:61
105:48:abaa
105:57:a2a6
105:63:a1
105:68:a6a2
105:74:40
105:77:aaaba6a5a3
106:48:a3a6a6a4
106:57:a0a4404040407070
106:68:a4a0
106:75:a4a6a6a3a2a1
106:82:a1a0
107:48:a01010a2a0
107:58:12
107:61:4070717170
107:68:a3
107:74:a0a2a1a1a0
107:81:a0a4a2a0
108:59:40
108:62:707170704040
108:80:a0a2a1a1a0
109:59:71404071727170707171
109:80:a0
109:83:a3a4a2a2
110:58:407271717171717272727040
110:82:a3a7a9a7a4
111:58:407071727345737472717040
111:80:10a4a8aa
111:85:a5a5
112:48:a1
112:59:7070727318467371707071
112:78:10a3a6a9
112:84:1311a2
113:48:a2a1
113:60:70717246457270
113:68:717140
113:77:a1a3a5
113:81:13
113:89:30
114:61:717072727371
114:69:7040
114:89:30
115:63:707272
115:68:7070
115:79:a0a0a0a0a0
116:48:a0
116:63:72727271707071
116:78:a0a2a2a2
117:65:40407071
118:48:a1
118:78:a1a3a515
119:48:a7a4a2
119:76:a2a4a7aa1b
119:82:16
120:48:a310
120:77:10a3a7a8
120:82:a4
121:79:10a2a412
123:48:a1a1
123:77:a1a1
123:89:30
124:48:a2a0
124:77:a0a2
124:85:30
125:50:4044a6a4
125:73:a4464440
126:48:a4a6a9a813
126:74:13a8a9a6a4a1
126:87:30
127:48:aa
127:51:107072
127:74:7010
127:78:aaa7
128:48:a8a4
128:52:40
128:74:40
128:77:a4a8a5
128:87:30
129:48:11
129:78:11a0
129:86:3030
129:90:0101
130:50:40
130:55:a0
130:70:40a040
130:89:30
130:92:010101
131:55:a5a0
131:60:a2
131:66:a2
131:70:41a5
131:73:40
131:82:303030
131:87:3030
131:94:0101
132:53:a0
132:55:a8
132:60:a6
132:66:a6
132:70:40a8
132:73:a0
132:89:30
132:95:01
133:52:a0
133:54:aaa6
133:58:40
133:60:aa10
133:65:10aa
133:68:40
133:70:40a6aa
133:74:a0
133:95:01
134:51:10
134:54:a8a2
134:59:a11ba3
134:65:a31ba1
134:70:70a2a8
134:75:10
135:51:11
135:54:13a0
135:59:a3aaa5
135:65:a5aaa3
135:70:70a013
135:75:a1
136:51:a4a3
136:57:70
136:59:a4
136:67:a4
136:69:7070
136:73:a1a3a4
136:86:30
137:54:4141
137:58:a1a5a613
137:65:13a6a5a1
137:71:4141
137:80:a1
137:87:30
138:58:a2
138:61:11
138:65:11
138:68:a2
138:85:303030
139:60:a3
139:62:70
139:64:70
139:66:a34443
"""

OPEN_233 = """
95:79:01
96:57:01
96:69:01
97:54:01a2a6a7a1a0
97:67:a0a1a7a6a201
98:53:01a2a5a9a9a5a2
98:67:a2a5a9a9a6a201
98:83:01
99:54:a4a4aaa9a443
99:67:43a4a9aaa4a4
100:51:01
100:54:41a2a8a9a54201
100:66:0142a5a9a8a2a2
100:75:01
101:49:0101a101
101:54:0101a5a9a64101
101:62:a0a1a0
101:66:0141a6a9a501
101:74:01a10101
101:79:a0
102:48:a3a001a1a2
102:55:01a2a6a640
102:61:01a1a4a101
102:67:40a6a6a201
102:74:a2a101a0a3a4a8
103:49:a1
103:52:a2
103:56:01a4a601
103:62:a1a2a1
103:67:01a6a401
103:74:a2
103:77:a1
103:79:a8a9
104:48:a9a401
104:53:01
104:56:01a2a6
104:62:01a201
104:68:a6a201
104:73:01
104:76:01a4a9
104:80:a5
105:48:a8a8a5
105:57:01a4
105:60:4040
105:63:a0
105:68:a401
105:74:70
105:76:a5a8a8a4a3a101
106:48:a0a0a101
106:57:01a2707070707171
106:68:a201
106:75:01a1a0a0010101a001
107:48:010101a101
107:58:70
107:60:407072737371
107:68:a2
107:74:01a1a0a00101
107:81:01a3a101
108:59:70
108:62:717271717070
108:80:01a1a0a00101
109:58:7172707073757372727272
109:79:010101
109:83:a2a3a1a1
110:48:01
110:58:707372727374737474747270
110:78:01
110:82:01a4a7a6a3
111:58:707273737578767775737270
111:80:01a0a5a8
111:85:a4a4
112:48:a0
112:59:717275777c797774717172
112:78:01a0a3a7
112:84:a4a1a1
113:48:01a0
113:60:71737679787571
113:68:727270
113:77:a0a0a3a4a3
113:85:01
114:60:71727275757572
114:68:727270
115:61:71
115:63:717373
115:67:72717171
115:79:010101010101
116:48:01
116:62:7273747372727172
116:78:01a1a1a101
117:63:717170707172
118:48:01
118:67:71
118:78:01a1a3a5
119:48:a4a201
119:76:01a2a4a8aa
119:82:a7
120:48:a00101
120:76:0101a0a4a7a7a6
121:48:01
121:78:0101a0a1a4
123:48:a0a0
123:77:a0a0
124:48:a101
124:77:01a1
125:48:01
125:50:7072a5a3
125:73:a3737270
125:78:0101
126:48:0101a4a5a372
126:74:a3a5a4010101
127:48:a8
127:50:a8a27173
127:74:71a2a8
127:78:a8a5
128:48:a9a5
128:52:70
128:74:70
128:77:a5a9a4
129:48:a1
129:78:a101
129:90:0101
130:50:01
130:55:0101
130:70:700101
130:92:010101
131:54:010101
131:60:a1
131:66:a1
131:70:70010170
131:94:0101
132:53:01a70101
132:60:a101
132:65:01a1
132:70:7001a701
132:95:01
133:52:01a4ac0101
133:58:7001a8017070
133:65:01a80170
133:70:7001aca401
133:95:01
134:51:01
134:54:a901
134:59:01aaa0
134:65:a0aa01
134:70:7101a9
134:75:01
135:51:a1a4a4a301
135:59:a1a9a3
135:65:a3a9a1
135:70:7101a3a4a4a0
136:51:a3a2
136:54:01
136:57:71
136:59:a2a9a4
136:65:a4a9a2
136:69:7171
136:72:01a0a2a3
137:54:0101
137:58:01a4a6a3
137:65:a3a6a401
137:71:0101
137:80:a0
138:58:a1a4a5a2
138:65:a2a5a4a1
139:60:a4
139:62:71
139:64:71
139:66:a4a3a1
"""

OPEN_237 = """
93:79:30
94:79:30
95:81:30
95:87:30
96:86:30
97:55:10a5a6a0a0
97:67:a0a0a6a510
97:82:30
97:85:30
98:53:0110a3a8a8a312
98:67:12a3a8a8a41001
98:83:013030
99:54:a2a2a8a8a343
99:67:43a3a8a8a2a2
99:84:30
100:51:01
100:54:4010a5a8a44201
100:66:0142a4a8a51010
100:75:01
101:49:0101a001
101:54:4001a2a6a51001
101:62:a0a0a0
101:66:0110a5a6a201
101:74:01a00101
101:79:a0
102:48:a1a001a010
102:55:0110a4a501
102:61:01a0a3a001
102:67:01a5a41001
102:74:10a001a0a113a7
103:48:a4a0
103:52:10
103:56:01a2a501
103:62:a010a0
103:67:01a5a201
103:74:10
103:77:a0a4a7a912
104:48:a7a301
104:53:01
104:56:0110a4
104:62:011001
104:68:a41001
104:73:01
104:76:01a3a7a8a3a2
105:48:04a5a3
105:52:40
105:57:01a2
105:63:40
105:65:40
105:68:a201
105:74:70
105:76:a3a504a2a1a001
106:48:a0a0a001
106:57:01104070407071717071404101
106:75:01a0a0a0010101a001
107:48:010101a001
107:58:4070
107:61:407272737272724340
107:74:01a0a0a00101
107:81:01a2a0
108:58:4040
108:61:727273727273737370
108:80:01a0a0a0
109:58:71727272747574737274737070
109:79:010101
109:83:10a2a0a0
110:48:01
110:56:40407073727447787575757473717040
110:78:01
110:82:01a2a4a5a2
111:55:407170727273494b4d7a78757472727370
111:80:01a0a2a5a7a5a3
112:48:a0
112:55:407272727273794b7e7a77747273754571
112:78:01a0a1a4a6
112:84:13a1a0
113:48:01a0
113:56:70737473727578797774727347757472
113:77:a0a0a1a2a2a1
113:89:30
114:56:707146747375747675747273487472
114:89:30
115:57:7173747474727273727274747272
115:79:0101010101
116:48:01
116:57:7272724646477474727272727272
116:78:01a0a0a001
117:57:727372451847187472717172
118:48:01
118:58:73727372737272717171
118:78:01a0a1a4
119:48:a31001
119:63:7171
119:76:0110a3a5a8a8a6
120:48:a00101
120:76:0101a0a2a4a6a5
121:48:01
121:78:0101a0a0a3
123:48:a0a0
123:77:a0a0
123:89:30
124:48:a001
124:77:01a0
124:85:30
125:48:01
125:50:707244a2
125:73:a2737270
125:78:0101
126:48:0101a3a4a272
126:74:a2a4a3010101
126:87:30
127:48:04a7a5a17172
127:74:71a1a5a704a2
128:48:a9a5
128:51:7070
128:74:7070
128:77:a5a9a4
128:87:30
129:48:11
129:51:40
129:75:40
129:78:11a3
129:86:3030
129:90:0101
130:50:40
130:54:400140
130:70:700101
130:89:30
130:92:010101
131:53:40010140
131:60:a0
131:66:a0
131:70:70010170
131:82:303030
131:87:3030
131:94:0101
132:53:40a40140
132:60:a001
132:65:01a0
132:70:7001a440
132:89:30
132:95:01
133:52:01a2
133:55:0140
133:58:700104017070
133:65:01040170
133:70:7001
133:73:a201
133:95:01
134:51:01a1a4a90170
134:59:01a8a0
134:65:a0a801
134:70:7101a9a4a101
135:51:a0a213a50170
135:59:a0a8a1
135:65:a1a8a0
135:70:7101a513a2a0
136:51:a2101001
136:56:7071
136:59:10
136:61:a2
136:65:a2
136:67:10
136:69:7171
136:72:01a010a2
136:86:30
137:54:0101
137:58:01a2a6a2
137:65:a2a6a201
137:71:0101
137:80:a0
137:87:30
138:58:a0a3a410
138:65:10a4a3a0
138:85:303030
139:58:4243a3
139:62:71
139:64:71
139:66:a3a2a0
"""

OPEN_241 = """
95:79:01
96:57:01
96:69:01
97:54:0101a3a40101
97:67:0101a4a30101
98:53:0101a1a7a6a143
98:67:43a1a6a7a10101
98:83:01
99:54:0101a5a6a242
99:67:42a2a6a50101
100:51:01
100:54:0101a2a6a34101
100:66:0141a3a6a20101
100:75:01
101:49:01010101
101:55:0101a3a34001
101:62:010101
101:66:0140a3a30101
101:74:01010101
101:79:01
102:48:0101010101
102:55:0101a1a301
102:61:0101a10101
102:67:01a3a10101
102:74:0101010101a3a5
103:48:a101
103:52:01
103:56:0101a301
103:62:010101
103:67:01a30101
103:74:01
103:77:01a1a6a8a2
104:48:a5a201
104:53:01
104:56:0101a1
104:62:010101
104:68:a10101
104:73:01
104:76:01a2a5a5a1a0
105:48:01a2a0
105:52:70
105:57:0101
105:63:70
105:65:70
105:68:0101
105:74:70
105:76:a0a20101010101
106:48:01010101
106:57:0101
106:60:70
106:62:7071717273707001
106:75:010101010101010101
107:48:0101010101
107:58:0171
107:61:407172737476757370
107:74:010101010101
107:81:01a00101
108:58:014040747474747375757572
108:80:010101010101
109:59:717473767675747376757271
109:79:010101
109:83:01a00101
110:48:01
110:56:707070737276797a7876777574727270
110:78:01
110:82:0101a1a3a0
111:55:7072727373747b7e7f7d79757572737571
111:80:010101a2a5
111:86:a1
112:48:01
112:55:7074747574757b7e7f7c7674747577787371
112:78:010101a0a4a5
112:85:a101
113:48:0101
113:55:7172767776747879797673737579787773
113:77:010101a0a1a001
113:85:01
114:56:7174797776777677767473767a767471
115:56:71737778777773747472737677747372
115:79:010101010101
116:48:01
116:56:72747576797979757572727374727371
116:78:0101010101
117:57:747675787c7a7b7774727272
117:70:71
118:48:01
118:57:7275747575777676737271
118:78:010101a2
119:48:a10101
119:58:7272727271727272
119:76:0101a1a1a5a7a4
120:48:010101
120:76:01010101a1a4a3
121:48:01
121:78:01010101a1
123:48:0101
123:77:0101
124:48:0101
124:77:0101
125:48:01
125:50:707273a0
125:73:a0737270
125:78:0101
126:48:0101a1a2a0
126:74:a0a2a1010101
127:48:01a1a2a071
127:74:71a0a2a10101
128:48:a8a5
128:51:7170
128:74:7071
128:77:a5a8a5
129:51:70
129:75:70
129:79:a6
129:90:0101
130:54:010170
130:70:700101
130:92:010101
131:53:70010170
131:60:01
131:66:01
131:70:70010170
131:94:0101
132:53:70010170
132:60:0101
132:65:0101
132:70:70010170
132:95:01
133:52:0101a40170
133:58:70010101
133:63:70
133:65:01010170
133:70:7001a40101
133:95:01
134:51:0101a1a90171
134:59:01a501
134:65:01a501
134:70:7101a9a10101
135:51:01a0a3a60171
135:59:01a701
135:65:01a701
135:70:7101a6a3a001
136:51:a0010101
136:56:7171
136:59:01a6a0
136:65:a0a601
136:69:7171
136:72:010101a0
137:54:0101
137:58:0101a6a1
137:65:a1a60101
137:71:0101
137:80:01
138:58:01a1a301
138:65:01a3a101
139:58:01a0a1
139:62:71
139:64:71
139:66:a1a001
"""

CLAW_163 = """
........010101..................................
........01666760................................
........0166676801..............................
........0166656867010101........................
........016665666866656501......................
........016666656566666601......................
......0165666765656565666501....................
......0166676965656565656501....................
....016567696866666566650101....................
....0165696967666667666465......................
....01656a6866666866640101......................
....01656b6a696867616101016001..................
....0164676b6a686362656365676501................
....01636466656562633534663c696601..............
....016463646463616364356788676601..............
016060666768666360306234656864..01..............
016968676a6b6a696765606265666401................
01696566676a6563636364010265020101..............
0169656667686563636363010101656601..............
0167666567686563626363010165646701..............
0164676567686563626201..606a646501..............
0162666668676462616301..606a67630101............
..606367686663620101....60696a666501............
..0162666966636201......0165676a6801............
....01636766636201......010101656701............
....01636765636201..........01016701............
......016467646301............016801............
......016366646301............616901............
........0166676301..........01676501............
........0163676460..........616501..............
..........0164656001......016501................
............60646401......0101..................
..............01646201..........................
................01010101........................
................................................
................................................
................................................
................................................
................................................
................................................
................................................
................................................
................................................
................................................
................................................
................................................
................................................
................................................
................................................
................................................
................................................
................................................
................................................
................................................
................................................
................................................
"""

CLAW_203 = """
........010101..................................
........01666760................................
........0166676801..............................
........0166656867010101........................
........016665666866656501......................
........016666656566666601......................
......0165666765656565666501....................
......0166676965656565656501....................
....016567696866666566650101016001..............
....0165696967666667666465..65676501............
....01656a6866666866640101..663c696601..........
....01656b6a69686761610101656788676601..........
....0164676b6a68636265630164656864..01..........
....01636466656562633534010165666401............
....0164636464636163643563010265020101..........
016060666768666360306234620101..01656601........
016968676a6b6a69676560623401..0165646701........
01696566676a6563636364010101..606a646501........
016965666768656363636301......606a67630101......
016766656768656362636301......60696a666501......
0164676567686563626201........0165676a6801......
0162666668676462616301........010101656701......
..606367686663620101..............01016701......
..0162666966636201..................016801......
....01636766636201..................616901......
....01636765636201................01676501......
......016467646301................616501........
......016366646301..............016501..........
........0166676301..............0101............
........0163676460..............................
..........0164656001............................
............60646401............................
..............01646201..........................
................01010101........................
................................................
................................................
................................................
................................................
................................................
................................................
................................................
................................................
................................................
................................................
................................................
................................................
................................................
................................................
................................................
................................................
................................................
................................................
................................................
................................................
................................................
................................................
"""

CLAW_207 = """
........010101..................................
........01666760................................
........0166676801..............................
........0166656867010101........................
........016665666866656501......................
........016666656566666601......................
......0165666765656565666501..01016001..........
......0166676965656565656501010165676501........
....01656769686666656665656465..663c696601......
....01656969676666676664636301..6788676601......
....01656a6866666866640101010165656864..01......
....01656b6a696867616101....016465666401........
....0164676b6a686362656301....010265020101......
....0163646665656263353401......01..01656601....
....016463646463616364356301......0165646701....
0160606667686663603062346201......606a646501....
016968676a6b6a69676560623401......606a67630101..
01696566676a6563636364010101......60696a666501..
016965666768656363636301..........0165676a6801..
016766656768656362636301..........010101656701..
0164676567686563626201................01016701..
0162666668676462616301..................016801..
..606367686663620101....................616901..
..0162666966636201....................01676501..
....01636766636201....................616501....
....01636765636201..................016501......
......016467646301..................0101........
......016366646301..............................
........0166676301..............................
........0163676460..............................
..........0164656001............................
............60646401............................
..............01646201..........................
................01010101........................
................................................
................................................
................................................
................................................
................................................
................................................
................................................
................................................
................................................
................................................
................................................
................................................
................................................
................................................
................................................
................................................
................................................
................................................
................................................
................................................
................................................
................................................
"""


if __name__ == "__main__":
    build()
