"""The Dragonwing's Dragon Flame (shots2 sprites 125, 126, 123 and 124; 55-57, 17-19, 74-76 and 36-38; 9-12 and 28-31,
all 1x1: 12 x 14 cells), modelled (2026-10-30, the third round of the energy shots' models; until then each was drawn as
its sprite with volume and the automatic glow). Built with polish_shot_fireball.py's kit (the pulse's method:
half-bodies on their bands' borders, palette materials glowing by shade, a raised core) and polish_shot_zflame.py's (the
fire wall is built as the Zica Flamethrower's flames are); the shots of several sprites are built whole and cut into the
pieces the game moves together.

Who fires them: the Dragon Flame (weapon port 47, the Dragonwing's gun: the second player's ship in arcade two-player
games; not sold, but a one-player game fires it too: TYR3D_WEAPONS=47,0,<power>), weapons 1013-1023 for power 1-11, the
same in all five episodes, straight up the screen through whatever they hit (the pieces' attack 251):
  power 1-3: 125 (5 pixels a tick; at 2 at bx -3 and +3 by turns, at 3 at six places from -3 to +3)
  power 4-5: 126 (7 pixels a tick; at 5 at -3 and +3)
  power 6-8: 123 and 124 by turns (weapani 1: two frames; 8 pixels a tick; at 7 at -5 and +5, at 8 at -2 8 -8 2)
  power 9-10: the 2 x 2 flame (9 pixels a tick, every 9 or 7 ticks): 55 at bx -8 by -7 (top left), 17 at +4 -7 (top
             right), 74 at -8 +7 (bottom left), 36 at +4 +7 (bottom right), every other volley 4 pixels to the right;
             weapani 2: three frames, 55 17 74 36, 56 18 75 37, 57 19 76 38 (the third the first's pixels again)
  power 11:  the fire wall (10 pixels a tick, every 13 ticks): 9 10 11 12 at bx -18 -6 6 18 by -7, 28 29 30 31 below
             at by +7: one 48 x 28 wall in eight pieces
As the sprites draw them (ramp 7, the fire: 0x70 black-red .. 0x77 red .. 0x7a orange .. 0x7c yellow .. 0x7f white):
- 125 a small drop of fire 5 pixels wide (columns 4-8, rows 2-10), a white-yellow heart (0x7e) in its round head, orange
  round it, a dark red rim, a short tail (0x72-0x79 down its middle); 126 the same a pixel wider, its heart left of its
  middle, its tail longer and darker (to row 12).
- 123 and 124 a larger flame (10 pixels wide, rows 0-13): a white heart (0x7f) high in a broad head, yellow and orange
  round it, an orange-red rim, the head narrowing into a tail with a bright streak down its middle (0x7b-0x7d); 124 the
  same flickering, a pixel to the left.
- the 2 x 2 flame: one 16 x 27 teardrop of fire (columns 4-19, rows 1-27 of the 24 x 28), its broad head white-hot
  (0x7e, 0x7f) over most of it inside yellow, orange and a dark red rim (0x73), its tail narrowing to a point with a
  bright streak down its middle; the second frame's heat moved about.
- the fire wall: an arch of fire 44 x 26 (columns 2-45, rows 2-27 of the 48 x 28), its top edge a smooth arc from the
  ends' row 12 to the middle's row 2, rimmed in black-red (0x70-0x72), hot clumps (0x7c-0x7f) along its upper band,
  orange and red below them, its lower edge ragged: tongues of dark red hanging down, the longest at its two ends (to
  row 27), an open notch in its middle below row 17.

The models:
- the drops (shot_dflame_125, _126, _123, _124) and the 2 x 2 flame's two frames: polish_shot_fireball.build_drop with a
  spec fitted to the sprite (drop_spec): the body round on top and flat underneath, lofted along the screen's y from
  the sprite's rows' half-widths (smoothed, a round nose); its heat round the hottest pixels (kit.blob_heat: the
  sprite's median shade in rings of distance from the hot spot, never rising outwards) or, down the tail, the sprite's
  hottest middle pixel row by row falling to its edge pixels' shades at the sides (a hot streak), whichever is hotter;
  a raised core on the hot spot (0x7f/0x7e, 0x7e/0x7d by the sprite's hottest shade); beads (raised hotter spots, the
  shared bands) on the head's other hot spots (one on 123 and 124, three on the 2 x 2 flame).
- the 2 x 2 flame built whole (24 x 28) and cut into its four sprites' pieces (open cuts, as the Zica's: never seen),
  each moved onto its sprite's centre (shot_dflame_55 17 74 36 and 56 18 75 37; the third frame's lines take the first
  frame's models).
- the fire wall (48 x 28) built whole as the Zica Flamethrower's flames are: a low dome (the bed) round its hot middle
  (WALL_CENTRE) over the sprite's extent by angle from there (mask_polar: marching out over the sprite's pixels, so its
  notch stays open), its heat the sprite's blurred over WALL_SIGMA_BED pixels (never rising outwards, at most
  WALL_BED_MAX); billows on its hot spots (WALL_BILLOWS, hottest first, as the Zica's); tongues where the sprite reaches
  beyond the dome (each connected group of its pixels there a thin loft hanging down the screen from inside the dome to
  the group's lowest pixel, its heat the sprite's down it); cut into the eight pieces (shot_dflame_9 10 11 12, 28 29 30
  31).
The pieces' model lines take "origin", their shot lines height= half their whole's height down; one glow a shot (on its
top left piece for the 2 x 2 flame, on 10 for the wall, the others glow=1:0). 200-1 244 triangles a model, 6-10
materials (BANDS: eight bands of ramp 7 shared by every model, emission 0.22-0.58 by shade, and two core materials).

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera; a drop's origin at
its sprite's centre (pixel 6, 7), a whole of several sprites built round its middle (its column c, row r: x = c + 0.5 -
w/2, y = h/2 - 0.5 - r), each piece moved onto its own sprite's centre; built on z = 0.

models.cfg: see the block's comment; --cfg <file> appends the model and shot lines (heights and glows as built).

Run: Blender -b --factory-startup -P tools/blender/models/shots/polish_shot_dflame.py -- [--only <name,...>]
     [--outdir <dir>] (default assets/models/shots) [--check <sheets dir>] (the silhouettes against the sprites in
     <dir>/shots2.png, from TYR3D_EXTRACT: a drop's, a whole's against its sprites side by side, each piece's)
     [--preview <prefix>] (top, three-quarter and game-camera views) [--cfg <file>]
"""
import math
import os
import sys

import bpy
import numpy as np
from mathutils import Matrix

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polish_shot_fireball as kit  # noqa: E402
from polish_shot_fireball import k, mk, triangulate, view  # noqa: E402
from polish_shot_zflame import cut_open, prune  # noqa: E402

# The sprites as their shades of the fire's ramp 7 (one hex digit a pixel, '.' transparent): the drops (12 x 14), the
# 2 x 2 flame's two frames (24 x 28: 55 17 above 74 36; 56 18 above 75 37) and the fire wall (48 x 28: 9 10 11 12 above
# 28 29 30 31).
ART = {
    '125': """
............
............
.....353....
....3aba3...
....5beb5...
....39db3...
.....7b9....
.....386....
.....292....
.....121....
......1.....
............
............
............
""",
    '126': """
............
............
....3a94....
...3aba73...
...5be994...
...3bd973...
....9ba42...
....5973....
....2522....
....1212....
.....21.....
......3.....
......2.....
............
""",
    '123': """
.....866....
...48bca87..
..78cdfba76.
.47acdec965.
.47acdea944.
.498bcb974..
.368add683..
..559db5a...
...67c978...
...559b65...
....44b6....
.....4b4....
......73....
......3.....
""",
    '124': """
....668.....
..78acb84...
.67abfdc87..
.569cedca74.
.449aedca74.
..479bcb894.
..386dda863.
...a5bd955..
...879c76...
...56b955...
....6b44....
....4b4.....
....37......
.....3......
""",
    'big0': """
........................
.........3354664........
........346565643.......
.......36779887643......
.......59abaccc985......
......379cbdddced64.....
.....369cbcfdbdcc74.....
....347ccbeffdeb864.....
....358bcfeffefca64.....
....468cceeefefec84.....
....357ecfbddfcfb94.....
....346fefccbcceba4.....
....3359cfcdbaad8b3.....
.....476afefc88a69......
.....4858ccff68767......
......746abfe9865.......
......4368bee8744.......
......3457abb774........
.......367b9d483........
.......355c9b5a.........
........3488978.........
.........357b65.........
.........348b6..........
..........58b4..........
..........6673..........
..........733...........
..........44............
..........3.............
""",
    'big1': """
........................
.........3354664........
........345454643.......
.......36767577543......
.......59abaccc8753.....
......379cbdddbba64.....
.....36acbcfdbca975.....
....347fcbeffdee8663....
....358fdfdfeeffa753....
....468cfeccceffcc54....
....3579efbddfcfbf64....
....3469efdeedcebc63....
.....356cfddeaad8843....
......46afeee88a674.....
......478cdff7a768......
......496acfdbb857......
......3668dcdbb94.......
.......557dbbb97........
........67cdf753........
........559df64.........
.........44ef76.........
..........48d69.........
...........6767.........
...........7844.........
...........6a3..........
...........43...........
........................
........................
""",
    'wall': """
................................................
................................................
..............000101000000111111102.............
...........001235544400255675213444410..........
..........0136accccb858aa66995224467530.........
........00257cdcabdffadfda7bb847764644210.......
.......12368abb979cfdadffb79a86aa944562320......
......2469a99a8778aeb7bcca76864bd9456575320.....
.....1678aca9a9888bc99cd79ba666bdb54679a7220....
....15867ac6aeb9acdb6aec9eeda668b98a64ab76220...
...048a889a3cfc8cfdb7ac96efdb89769bbb39a766410..
...26ac99a94aea8bdd87ba86bedb79bcbbdb587467640..
..0169b9bdb57b78aba69a8778bcb79cfcacc5774567620.
..0148a9dec66857aa9799765479b76aba9ac5665445620.
..0169779ea64747aa8787554468a468a949b6798743720.
..019c828c96553899778533147aa5679848a59cb856730.
..039e937a87653798888310039de855873673588567920.
..039a925968962798766200.26b9435862557555359820.
..2579524848a6159512410...46413375346976424a930.
..1686314867a4048301310...25202363246a88514ab51.
..0695203a67721372..210...141..1520367675128a61.
..0796103a85410241...00...12...0300235453115872.
..06841.3a841..12.....0...0.....10..04332.03572.
..1451..2760....1...............0....1221..2552.
..0330..141...........................010..2350.
..010...01.............................00...230.
...00...0...............................0...11..
...0.........................................0..
""",
}

# The fire's bands, shared by every model: (lowest heat, palette index, emission strength), ramp 7 from the tongues'
# dark red to the yellow round the cores; the heat is in the sprites' shades (0-15). The cores' bands from their middle
# out, by the sprite's hottest shade.
BANDS = [(-99.0, 0x72, 0.22), (2.5, 0x74, 0.26), (4.5, 0x76, 0.33), (6.5, 0x78, 0.40), (8.3, 0x7a, 0.48),
         (9.8, 0x7b, 0.52), (11.2, 0x7c, 0.56), (12.5, 0x7d, 0.58)]
# The shots whose hottest parts are billows (the 2 x 2 flame, the wall) have no core: their bands go on to white.
BANDS_HOT = BANDS + [(13.6, 0x7e, 0.6), (14.5, 0x7f, 0.62)]
CORE_BANDS = {15: ((0.0, 0x7f, 0.62), (0.5, 0x7e, 0.6)), 14: ((0.0, 0x7e, 0.6), (0.5, 0x7d, 0.58)),
              13: ((0.0, 0x7d, 0.58), (0.5, 0x7c, 0.56))}
DEPTH = 0.86


class Art:
    """A sprite (or several side by side) as shades: S (rows from the top, nan transparent), its size and the model
    coordinates of its pixels (x right, y up, the origin at its middle)."""

    def __init__(self, key):
        rows = ART[key].strip("\n").splitlines()
        self.S = np.array([[np.nan if ch == "." else float(int(ch, 16)) for ch in r] for r in rows])
        self.h, self.w = self.S.shape

    def x(self, c):
        return c + 0.5 - self.w / 2

    def y(self, r):
        return self.h / 2 - 0.5 - r

    def pixels(self):
        rr, cc = np.where(~np.isnan(self.S))
        return [(self.x(c), self.y(r), float(self.S[r, c])) for r, c in zip(rr, cc)]

    def rows(self):
        """[(row, first column, last column)] of the rows that have pixels."""
        out = []
        for r in range(self.h):
            cols = np.where(~np.isnan(self.S[r]))[0]
            if len(cols):
                out.append((r, int(cols[0]), int(cols[-1])))
        return out


def hot_centre(pixels, within=2.0):
    top = max(s for _, _, s in pixels)
    hot = [(x, y, (s - (top - within - 1)) ** 2) for x, y, s in pixels if s >= top - within]
    total = sum(w for _, _, w in hot)
    return sum(x * w for x, _, w in hot) / total, sum(y * w for _, y, w in hot) / total


def smooth_list(values, passes=1):
    v = list(values)
    for _ in range(passes):
        v = [v[0]] + [0.25 * v[i - 1] + 0.5 * v[i] + 0.25 * v[i + 1] for i in range(1, len(v) - 1)] + [v[-1]]
    return v


def bead_bands(crown, rim):
    """A bead's bands from its middle out (dome_core's (from u, index, emission)): the shared bands its heat crosses,
    falling from crown at its middle to rim at its edge as 1 - u^1.4."""
    out, previous = [], None
    for lowest, index, glow in reversed(BANDS):
        if lowest >= crown:
            continue
        if not out:
            out.append((0.0, index, glow))
        else:
            u = ((crown - previous) / max(crown - rim, 1e-6)) ** (1 / 1.4)
            if u < 0.97:
                out.append((u, index, glow))
        previous = lowest
        if lowest <= rim:
            break
    return tuple(out)


def find_beads(art, field, centre, count, apart, radius, least):
    """The sprite's hot spots (the blurred shades' local maxima, hottest first, at least `least`, apart pixels from the
    core's centre and from each other): [(x, y, heat there)]."""
    found = []
    for r in range(art.h):
        for c in range(art.w):
            v = field[r, c]
            if np.isnan(v) or v < least:
                continue
            around = field[max(r - 1, 0):r + 2, max(c - 1, 0):c + 2]
            if v >= np.nanmax(around) - 1e-9:
                found.append((art.x(c), art.y(r), float(v)))
    found.sort(key=lambda p: (-p[2], p[0], p[1]))
    beads = []
    for x, y, v in found:
        if math.hypot(x - centre[0], y - centre[1]) < apart or any(math.hypot(x - b[0], y - b[1]) < apart
                                                                    for b in beads):
            continue
        beads.append((x, y, v))
        if len(beads) == count:
            break
    return beads


def drop_spec(art, segments=None, beads=0):
    """A drop of fire fitted to a sprite: build_drop's spec (the body lofted along the screen's y from the sprite's
    rows' half-widths, smoothed, round at its nose; its heat a field round the hottest pixels (kit.blob_heat: the
    sprite's median shades in rings round the hot spot, never rising outwards) or, down the tail, the sprite's middle
    pixels there (a hot streak) falling to the sides, whichever is hotter; a raised core on the hot spot; beads (hotter
    raised spots) on the head's other hot spots) and the sprite's hottest shade."""
    rows = art.rows()
    nose, tail = art.h / 2 - rows[0][0], art.h / 2 - rows[-1][0] - 1
    length = nose - tail
    widths = [(c1 - c0 + 1) / 2.0 for _, c0, c1 in rows]
    mids = [(art.x(c0) + art.x(c1)) / 2 for _, c0, c1 in rows]
    weights = [w ** 2 for w in widths]
    axis = sum(m * w for m, w in zip(mids, weights)) / sum(weights)
    ts = [(nose - art.y(r)) / length for r, _, _ in rows]
    ws = smooth_list(widths)
    width = [(0.0, 0.0), (0.15 * ts[0], 0.6 * ws[0]), (0.55 * ts[0], 0.88 * ws[0])]
    width += list(zip(ts, ws))
    width += [(ts[-1] + 0.5 * (1 - ts[-1]), 0.55 * ws[-1]), (1.0, 0.0)]
    half = kit.curve(width)
    pixels = art.pixels()
    peak = max(s for _, _, s in pixels)
    hx, hy = hot_centre(pixels)
    i_max = max(range(len(ws)), key=lambda i: (ws[i], -i))
    wmax = ws[i_max]
    neck = next((art.y(rows[i][0]) for i in range(i_max, len(rows)) if ws[i] < 0.6 * wmax), tail)
    rx, ry_up, ry_down = 0.95 * wmax, max(nose - hy, 1.0), max(hy - neck, 1.0)
    # The head's heat by the distance from the hot spot in its half-axes: the sprite's pixels' median shade in rings of
    # that distance, never rising outwards, the hottest shade in the middle.
    def dist(x, y):
        return math.hypot((x - hx) / rx, (y - hy) / (ry_up if y > hy else ry_down))
    rings = [[] for _ in range(7)]
    for x, y, v in pixels:
        if y >= neck:
            rings[min(int(dist(x, y) / 0.2), 6)].append(v)
    medians = [float(np.median(r)) if r else None for r in rings]
    profile, low = [(0.0, peak + 0.3)], peak + 0.3
    for i, m in enumerate(medians):
        if m is not None:
            low = min(low - 0.05, m)
            profile.append((0.2 * i + 0.1, low))
    profile += [(1.5, max(low - 1.5, 0.3)), (2.0, max(low - 2.5, 0.2))]
    blob = kit.blob_heat((hx, hy), rx, ry_up, ry_down, profile)
    # Down the tail: the hottest of its middle pixels row by row, falling to its edge pixels' shades at its sides.
    streak = []
    for r, c0, c1 in rows:
        y = art.y(r)
        if y >= hy - 0.5:
            continue
        near = [art.S[r, c] for c in range(art.w) if not np.isnan(art.S[r, c]) and abs(art.x(c) - axis) <= 1.2]
        middle = max(near) if near else 0.5
        streak.append((y, middle, max(middle - 0.5 * (art.S[r, c0] + art.S[r, c1]), 0.0)))
    streak.sort()
    line = None
    if len(streak) >= 2:
        line = kit.curve([(y, v) for y, v in zip([p[0] for p in streak], smooth_list([p[1] for p in streak]))])
        fall = kit.curve([(y, v) for y, v in zip([p[0] for p in streak], smooth_list([p[2] for p in streak]))])
        top = streak[-1][0]

    def heat(x, y):
        h = blob(x, y)
        if line is not None and y <= top:
            w = max(half((nose - y) / length), 0.5)
            u = min(abs(x - axis) / w, 1.3)
            h = max(h, line(y) - fall(y) * u * u)
        return h
    spec = dict(
        x=axis, nose=nose, tail=tail, depth=DEPTH, width=width, heat=heat,
        segments=segments or (8 if wmax <= 3 else 10 if wmax <= 5.5 else 12),
        waves=(2.5, 0.025, 1.9), tongues=[],
        core=(hx, hy, 0.3 * rx + 0.25, 0.3 * (ry_up + ry_down) / 2 + 0.25, 0.22 + 0.03 * wmax))
    if beads:
        field = smoothed(art.S, 1.0)
        spec["beads"] = []
        for bx, by, v in find_beads(art, field, (hx, hy), beads, 0.32 * (rx + ry_up), 0.0, peak - 3.5):
            br = 0.16 * rx + 0.35
            crown = 0.5 * v + 0.5 * peak - 0.5
            spec["beads"].append((bx, by, br, 1.1 * br, BEAD_LIFT * br, bead_bands(crown, heat(bx + br, by) - 0.3)))
    return spec, int(peak)


BEAD_LIFT = 0.3


# --- The fire wall (48 x 28, 8 pieces) --------------------------------------------------------------------------------

# The wall is built as the Zica Flamethrower's flames are (polish_shot_zflame.py): a low dome (the bed) over its shape
# round its hot middle, its heat the sprite's (blurred, never rising outwards), billows on its hot spots, and tongues
# (thin lofts) where the sprite's tongues reach beyond the dome. The dome's middle, height, profile and points round;
# the blurring (the billows', the bed's); the bed's heat at most and its fall outwards (as the Zica's); the billows'
# radius, lift, how many; the tongues' least size (pixels), their heat's fall to their sides, their roots' depth in
# the dome.
WALL_CENTRE, WALL_HEIGHT, WALL_POWER, WALL_SEGMENTS, WALL_SIGMA, WALL_SIGMA_BED, WALL_BED_MAX, WALL_BED_FALL = \
    (0.0, 5.5), 4.0, 0.6, 40, 1.2, 2.4, 9.6, 1.8
WALL_BILLOW_R, WALL_BILLOW_LIFT, WALL_BILLOWS = 3.6, 0.26, 14
WALL_TONGUE_LEAST, WALL_TONGUE_ACROSS, WALL_TONGUE_ROOT, WALL_TONGUE_DEPTH = 5, 2.0, 4.5, 0.5


def smoothed(S, sigma):
    """The shades blurred (a Gaussian of sigma pixels) within the sprite (nan outside)."""
    mask = (~np.isnan(S)).astype(float)
    v = np.nan_to_num(S) * mask
    reach = int(3 * sigma) + 1
    g = np.exp(-np.arange(-reach, reach + 1) ** 2 / (2.0 * sigma * sigma))

    def blur(a):
        a = np.apply_along_axis(lambda m: np.convolve(m, g, mode="same"), 0, a)
        return np.apply_along_axis(lambda m: np.convolve(m, g, mode="same"), 1, a)
    num, den = blur(v), blur(mask)
    return np.where(mask > 0, num / np.maximum(den, 1e-9), np.nan)


def sample(art, field, x, y):
    """A field over the sprite's pixels (rows from the top) at a point, bilinear; outside the sprite the nearest
    pixel's."""
    c, r = x + art.w / 2 - 0.5, art.h / 2 - 0.5 - y
    c0, r0 = int(math.floor(c)), int(math.floor(r))
    total, weight = 0.0, 0.0
    for dr in (0, 1):
        for dc in (0, 1):
            rr, cc = r0 + dr, c0 + dc
            if 0 <= rr < art.h and 0 <= cc < art.w and not np.isnan(field[rr, cc]):
                w = (1 - abs(r - rr)) * (1 - abs(c - cc))
                total += w * field[rr, cc]
                weight += w
    if weight > 1e-6:
        return total / weight
    rr, cc = np.where(~np.isnan(field))
    i = int(np.argmin((rr - r) ** 2 + (cc - c) ** 2))
    return float(field[rr[i], cc[i]])


def inside(art, x, y):
    c, r = int(math.floor(x + art.w / 2)), int(math.floor(art.h / 2 - y))
    return 0 <= r < art.h and 0 <= c < art.w and not np.isnan(art.S[r, c])


def mask_polar(art, centre, samples=240, step=0.25, gap=0.8, smooth=5.0):
    """The sprite's extent from centre by angle (marching out until more than gap pixels outside it), its steps smoothed
    over smooth degrees, interpolated."""
    raw = []
    for j in range(samples):
        phi = 2 * math.pi * j / samples
        r, last = 0.0, 0.0
        while r < 80.0:
            r += step
            if inside(art, centre[0] + r * math.cos(phi), centre[1] + r * math.sin(phi)):
                last = r
            elif r - last > gap:
                break
        raw.append(last + 0.5 * step)
    sigma = smooth / 360.0 * samples
    reach = int(3 * sigma) + 1
    weights = [math.exp(-d * d / (2 * sigma * sigma)) for d in range(-reach, reach + 1)]
    table = [sum(w * raw[(i + d) % samples] for w, d in zip(weights, range(-reach, reach + 1))) / sum(weights)
             for i in range(samples)]

    def radius(phi):
        f = (phi % (2 * math.pi)) / (2 * math.pi) * samples
        i = int(f) % samples
        a = f - int(f)
        return table[i] * (1 - a) + table[(i + 1) % samples] * a
    return radius


def billows_on(prefix, art, F, candidates, count, r0, lift_k, host_top, host_heat_xy, margin, bands, mats):
    """Billows (raised patches, as the Zica Flamethrower's), hottest first, on the candidate pixels (blurred heat F)
    that no billow covers yet: each round its middle (r0, clipped where margin(x, y), the host's outline at 1, passes
    0.97), standing lift_k * r0 out of host_top, its heat the blurred sprite (never rising outwards from its middle),
    its crown hotter (towards the hottest pixel near), its rim the host's heat there. Returns ([objects], [(x, y, r,
    crown)])."""
    from polish_shot_zflame import RayHeat, BILLOW_APART
    raw = art.pixels()
    pixels = [(x, y, sample(art, F, x, y)) for x, y in candidates]
    billows = []
    while len(billows) < count:
        free = [p for p in pixels if all(math.hypot(p[0] - b[0], p[1] - b[1]) > BILLOW_APART * 2 * b[2]
                                         for b in billows)]
        if not free:
            break
        x, y, h = max(free, key=lambda p: (p[2], -p[0], p[1]))
        near = max(v for px, py, v in raw if math.hypot(px - x, py - y) < 2.0)
        billows.append((x, y, r0, max(h + 0.6, h + 0.6 * (near - h))))
    parts = []
    for i, (bx, by, r, crown) in enumerate(billows):
        lift = lift_k * r

        def b_radius(phi, bx=bx, by=by, r=r):
            lo, hi = 0.0, r
            if margin(bx + hi * math.cos(phi), by + hi * math.sin(phi)) <= 0.97:
                return r
            for _ in range(24):
                mid = (lo + hi) / 2
                if margin(bx + mid * math.cos(phi), by + mid * math.sin(phi)) <= 0.97:
                    lo = mid
                else:
                    hi = mid
            return max(lo, 0.3)

        def b_top(x, y, bx=bx, by=by, b_radius=b_radius, lift=lift):
            dx, dy = x - bx, y - by
            d = math.hypot(dx, dy)
            q = d / max(b_radius(math.atan2(dy, dx)), 1e-6) if d > 1e-9 else 0.0
            return host_top(x, y) + lift * max(0.0, 1.0 - q * q) ** 0.5
        centre_heat = sample(art, F, bx, by)

        def b_profile(phi, u, bx=bx, by=by, b_radius=b_radius, crown=crown, centre_heat=centre_heat):
            rr = u * b_radius(phi)
            x, y = bx + rr * math.cos(phi), by + rr * math.sin(phi)
            own = sample(art, F, x, y) + (crown - centre_heat) * (1.0 - u) ** 1.5
            w = mk.smoothstep(0.6, 1.0, u)
            return own * (1 - w) + host_heat_xy(x, y) * w
        dome = kit.Dome((bx, by), b_radius, b_top, RayHeat(b_profile, rays=48, steps=30), bands, segments=10,
                        tongues=(3, 0.04, 1.0), gap=0.3, middle_fractions=(0.45,), rim_fractions=(0.55, 1.0))
        parts.append(prune(dome.build("%s_billow%d" % (prefix, i), mats)))
    return parts, billows


def build_wall(prefix):
    """The fire wall whole: the bed, its billows and its tongues."""
    from polish_shot_zflame import RayHeat
    art = Art("wall")
    F = smoothed(art.S, WALL_SIGMA)
    C = smoothed(art.S, WALL_SIGMA_BED)
    mats = kit.materials(prefix + "_fire", BANDS_HOT)
    cx, cy = WALL_CENTRE
    radius = mask_polar(art, WALL_CENTRE)

    def rho(x, y):
        dx, dy = x - cx, y - cy
        d = math.hypot(dx, dy)
        return d / max(radius(math.atan2(dy, dx)), 1e-6) if d > 1e-9 else 0.0

    def bed_top(x, y):
        return WALL_HEIGHT * max(0.0, 1.0 - rho(x, y) ** 2) ** WALL_POWER
    # The bed's heat: the blurred shades' mean over its inner half in its middle (at most WALL_BED_MAX), falling to
    # theirs near its edge (by angle) as the WALL_BED_FALL power of the way out.
    inner = [sample(art, C, x, y) for x, y, _ in art.pixels() if rho(x, y) < 0.5]
    middle = min(WALL_BED_MAX, float(np.mean(inner)) + 0.5)
    rims = []
    for j in range(120):
        phi = 2 * math.pi * j / 120
        d = 0.85 * radius(phi)
        rims.append(sample(art, C, cx + d * math.cos(phi), cy + d * math.sin(phi)))
    rims = [min(middle - 0.3, sum(rims[(j + i) % 120] for i in range(-4, 5)) / 9) for j in range(120)]

    def bed_profile(phi, u):
        a = (phi % (2 * math.pi)) / (2 * math.pi) * 120
        i, t = int(a) % 120, a - int(a)
        rim = rims[i] * (1 - t) + rims[(i + 1) % 120] * t
        return middle - (middle - rim) * min(max(u, 0.0), 1.0) ** WALL_BED_FALL
    bed_heat = RayHeat(bed_profile, rays=120, steps=40)

    def bed_heat_xy(x, y):
        return bed_heat(rho(x, y), math.atan2(y - cy, x - cx))
    bed = kit.Dome(WALL_CENTRE, radius, bed_top, bed_heat, BANDS_HOT, segments=WALL_SEGMENTS, tongues=(9, 0.03, 1.3),
                   gap=0.25, middle_fractions=(0.5,), rim_fractions=(0.5, 0.82, 1.0))
    parts = [prune(bed.build(prefix + "_bed", mats))]
    candidates = [(x, y) for x, y, _ in art.pixels() if rho(x, y) < 0.9]
    more, billows = billows_on(prefix, art, F, candidates, WALL_BILLOWS, WALL_BILLOW_R, WALL_BILLOW_LIFT, bed_top,
                               bed_heat_xy, rho, BANDS_HOT, mats)
    parts += more
    # The tongues: the sprite's pixels beyond the dome, in connected groups, each a thin loft hanging down the screen
    # from inside the dome to its lowest pixel.
    left = np.zeros_like(art.S, dtype=bool)
    for r in range(art.h):
        for c in range(art.w):
            if not np.isnan(art.S[r, c]) and rho(art.x(c), art.y(r)) > 0.92:
                left[r, c] = True
    seen = np.zeros_like(left)
    groups = []
    for r in range(art.h):
        for c in range(art.w):
            if left[r, c] and not seen[r, c]:
                stack, group = [(r, c)], []
                seen[r, c] = True
                while stack:
                    a, b = stack.pop()
                    group.append((a, b))
                    for da, db in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        aa, bb = a + da, b + db
                        if 0 <= aa < art.h and 0 <= bb < art.w and left[aa, bb] and not seen[aa, bb]:
                            seen[aa, bb] = True
                            stack.append((aa, bb))
                if len(group) >= WALL_TONGUE_LEAST:
                    groups.append(sorted(group))
    for i, group in enumerate(groups):
        rows = sorted({a for a, _ in group})
        x = float(np.mean([art.x(b) for _, b in group]))
        nose = art.h / 2 - rows[0] + WALL_TONGUE_ROOT
        tail = art.h / 2 - rows[-1] - 1
        length = nose - tail
        ts, ws, hs = [], [], []
        for a in rows:
            cols = [b for aa, b in group if aa == a]
            ts.append((nose - art.y(a)) / length)
            ws.append(len(cols) / 2.0 + 0.35)
            hs.append(max(sample(art, F, art.x(b), art.y(a)) for b in cols))
        ws = smooth_list(ws, 1)
        hs = smooth_list(hs, 1)
        for j in range(1, len(hs)):
            hs[j] = min(hs[j], hs[j - 1] - 1e-3)
        width = [(0.0, 0.0), (0.02, 0.55 * ws[0]), (0.06, 0.85 * ws[0])] + \
            [(t, w) for t, w in zip(ts, ws) if t > 0.07] + [(1.0, 0.0)]
        along = [(0.0, hs[0] + 0.2)] + list(zip(ts, hs)) + [(1.0, max(hs[-1] - 0.5, 0.0))]
        heat = kit.loft_heat(along, ((0.0, WALL_TONGUE_ACROSS), (1.0, WALL_TONGUE_ACROSS)))
        tongue = kit.Loft(x, nose, tail, kit.curve(width), heat, BANDS_HOT, depth=WALL_TONGUE_DEPTH, segments=6,
                          tongues=(2.0, 0.02, 1.2), gap=0.2, width_gap=0.5)
        parts.append(prune(tongue.build("%s_tongue%d" % (prefix, i), mats)))
    print("fire wall: %d billows, %d tongues" % (len(billows), len(groups)))
    global WALL_HOT
    WALL_HOT = billows[0][:2]
    return parts


WALL_HOT = (0.0, 0.0)  # (the hottest billow's middle: the wall's glow)


# --- The models -------------------------------------------------------------------------------------------------------

# Pieces of the shots of several sprites: (sprite, its box in the whole (x0, x1, y0, y1)).
BIG_PIECES = {0: [(55, (-12.0, 0.0, 0.0, 14.0)), (17, (0.0, 12.0, 0.0, 14.0)), (74, (-12.0, 0.0, -14.0, 0.0)),
                  (36, (0.0, 12.0, -14.0, 0.0))],
              1: [(56, (-12.0, 0.0, 0.0, 14.0)), (18, (0.0, 12.0, 0.0, 14.0)), (75, (-12.0, 0.0, -14.0, 0.0)),
                  (37, (0.0, 12.0, -14.0, 0.0))]}
WALL_PIECES = [(9, (-24.0, -12.0, 0.0, 14.0)), (10, (-12.0, 0.0, 0.0, 14.0)), (11, (0.0, 12.0, 0.0, 14.0)),
               (12, (12.0, 24.0, 0.0, 14.0)), (28, (-24.0, -12.0, -14.0, 0.0)), (29, (-12.0, 0.0, -14.0, 0.0)),
               (30, (0.0, 12.0, -14.0, 0.0)), (31, (12.0, 24.0, -14.0, 0.0))]
DROPS = [("shot_dflame_125", "125"), ("shot_dflame_126", "126"), ("shot_dflame_123", "123"), ("shot_dflame_124", "124")]


def build_drop_model(name, key, beads=0):
    spec, peak = drop_spec(Art(key), beads=beads)
    parts = kit.build_drop(name, spec, "dflame", BANDS, CORE_BANDS[min(max(peak, 13), 15)])
    return [prune(p) for p in parts], spec


# The 2 x 2 flame's head: its body's heat at most BIG_BODY_MAX, billows (as the Zica Flamethrower's) on its hot spots
# above the neck (BIG_BILLOWS at most, radius BIG_BILLOW_R, lift) carry the white.
BIG_BODY_MAX, BIG_BILLOWS, BIG_BILLOW_R, BIG_BILLOW_LIFT = 11.5, 7, 2.8, 0.3


def build_big(name, key):
    """The 2 x 2 flame whole: the drop's body (its heat capped) and billows on its head; (parts, spec, hot point)."""
    art = Art(key)
    spec, peak = drop_spec(art)
    field = spec["heat"]

    def heat(x, y):
        return min(BIG_BODY_MAX, field(x, y))
    mats = kit.materials("dflame_fire", BANDS_HOT)
    body = kit.Loft(spec["x"], spec["nose"], spec["tail"], kit.curve(spec["width"]), None, BANDS_HOT,
                    depth=spec["depth"], segments=spec["segments"], tongues=spec["waves"], gap=0.12, width_gap=0.6,
                    heat_xy=heat)
    parts = [prune(body.build(name + "_fire", mats))]
    half = kit.curve(spec["width"])

    def margin(x, y):
        t = (body.nose - y) / body.length
        if not 0.0 <= t <= 1.0:
            return 2.0
        return abs(x - body.x) / max(half(t), 1e-6)
    neck = spec["core"][1] - 0.6 * (spec["core"][1] - spec["tail"])
    candidates = [(x, y) for x, y, _ in art.pixels() if y > neck and margin(x, y) < 0.85]
    F = smoothed(art.S, 1.1)
    more, billows = billows_on(name, art, F, candidates, BIG_BILLOWS, BIG_BILLOW_R, BIG_BILLOW_LIFT, body.top, heat,
                               margin, BANDS_HOT, mats)
    print("%s: %d billows %s" % (name, len(billows), " ".join("(%.1f %.1f h%.1f)" % (b[0], b[1], b[3])
                                                               for b in billows)))
    return parts + more, spec, billows[0][:2]


def cut_pieces(whole, pieces, suffix):
    """The whole cut into its sprites' pieces (open cuts: the pieces are always drawn together), each moved onto its
    sprite's centre: {sprite: [objects]}."""
    out = {}
    for sprite, box in pieces:
        cx, cy = (box[0] + box[1]) / 2, (box[2] + box[3]) / 2
        parts = []
        for obj in whole:
            piece = cut_open(obj, box)
            if piece is None:
                continue
            piece.data.transform(Matrix.Translation((-cx, -cy, 0.0)))
            piece.name = "%s_%s%d" % (obj.name, suffix, sprite)
            parts.append(piece)
        out[sprite] = parts
    return out


def export_pieces(name_of, whole, pieces, options, sheets, size, label):
    outdir = options.get("outdir", kit.OUTDIR)
    only = set(options["only"].split(",")) if "only" in options else None
    height = max(v.co.z for o in whole for v in o.data.vertices)
    print("%s: whole %d triangles, height %.2f" % (label, mk.triangles(whole), height))
    if sheets:
        rows = [pieces[i:i + size[0] // 12] for i in range(0, len(pieces), size[0] // 12)]
        m = []
        for row in rows:
            masks = [k.sprite_mask(os.path.join(sheets, "shots2.png"), s, large=False) for s, _ in row]
            m += [sum((mm[y] for mm in masks), []) for y in range(14)]
        mk.compare(label, mk.coverage(whole, size[0], size[1]), m)
    if "preview" in options:
        bpy.context.scene.view_settings.view_transform = "Standard"
        view(options["preview"] + label.replace(" ", "_"), whole, size=size)
    cut = cut_pieces(whole, pieces, "b")
    for o in whole + [o for parts in cut.values() for o in parts]:
        o.hide_render = True
    lines = []
    for sprite, parts in cut.items():
        name = name_of(sprite)
        lines.append((sprite, name, height))
        if only is not None and name not in only:
            continue
        for o in parts:
            o.hide_render = False
        if sheets:
            mk.compare("%s (shots2 %d)" % (name, sprite), mk.coverage(parts, 12, 14),
                       k.sprite_mask(os.path.join(sheets, "shots2.png"), sprite, large=False))
        bpy.context.scene.view_settings.view_transform = "Standard"
        mk.report(name, parts, os.path.join(outdir, name + ".glb"))
        for o in parts:
            o.hide_render = True
    return lines


# The glows (glow=): (size, strength, palette index) for a drop, a 2 x 2 flame (on its top left piece, at the hot spot)
# and the wall (on its top middle left piece (shots2 10), at the hottest billow); the other pieces glow=1:0 (none).
GLOW_DROP = {"125": (11, 0.45, 0x7c), "126": (12, 0.45, 0x7c), "123": (16, 0.45, 0x7c), "124": (16, 0.45, 0x7c)}
GLOW_BIG = (22, 0.4, 0x7c)
GLOW_WALL = (34, 0.35, 0x7b)


def write_cfg(path, models, shots):
    with open(path, "a") as out:
        out.write("\n".join(models + shots) + "\n")


def piece_lines(pieces, name_of, height, glow, hot, glow_piece, also=()):
    """Model and shot lines of a shot's pieces (origin; height= half the whole's height down; the glow on one piece at
    the whole's hot point); also: [(sprite, the piece's sprite whose model it shows)] (frames that repeat one)."""
    models, shots = [], []
    for sprite, box in pieces:
        models.append("model %-15s shots/%s.glb origin" % (name_of(sprite), name_of(sprite)))
    for sprite, box in list(pieces) + [(s, dict(pieces)[t]) for s, t in also]:
        model = name_of(sprite if sprite in dict(pieces) else dict(also)[sprite])
        cx, cy = (box[0] + box[1]) / 2, (box[2] + box[3]) / 2
        if sprite == glow_piece or (sprite, glow_piece) in also:
            g = "glow=%d:%.2f:%d:%.2f:%.2f" % (glow[0], glow[1], glow[2], hot[0] - cx, cy - hot[1])
        else:
            g = "glow=1:0"
        shots.append("shot shots2 %-3d %-15s height=%.2f %s" % (sprite, model, -height / 2, g))
    return models, shots


def build():
    options = k.args()
    only = set(options["only"].split(",")) if "only" in options else None
    outdir = options.get("outdir", kit.OUTDIR)
    sheets = options.get("check")
    for name, key in DROPS:
        if only is not None and name not in only:
            continue
        k.reset()
        parts, spec = build_drop_model(name, key, beads=1 if key in ("123", "124") else 0)
        parts = triangulate(parts)
        bpy.context.view_layer.update()
        print("== %s (shots2 %s): a drop of fire, axis x %.2f, nose %.1f, tail %.1f, core %s" % (
            name, key, spec["x"], spec["nose"], spec["tail"], " ".join("%.2f" % v for v in spec["core"])))
        if sheets:
            kit.check_lines(name, parts, os.path.join(sheets, "shots2.png"), [(int(key), 0, 0, 0)], spec["core"][:2])
        bpy.context.scene.view_settings.view_transform = "Standard"
        mk.report(name, parts, os.path.join(outdir, name + ".glb"))
        if "cfg" in options:
            size, strength, colour = GLOW_DROP[key]
            write_cfg(options["cfg"], ["model %-15s shots/%s.glb" % (name, name)],
                      ["shot shots2 %-3s %-15s glow=%d:%.2f:%d:%.2f:%.2f" % (key, name, size, strength, colour,
                                                                           spec["core"][0], -spec["core"][1])])
        if "preview" in options:
            view(options["preview"] + name, parts)
    for frame, pieces in BIG_PIECES.items():
        names = ["shot_dflame_%d" % s for s, _ in pieces]
        if only is not None and not any(n in only for n in names):
            continue
        k.reset()
        parts, spec, hot = build_big("dflame_big%d" % frame, "big%d" % frame)
        whole = triangulate(parts)
        bpy.context.view_layer.update()
        height = max(v.co.z for o in whole for v in o.data.vertices)
        export_pieces(lambda s: "shot_dflame_%d" % s, whole, pieces, options, sheets, (24, 28),
                      "big flame frame %d" % frame)
        if "cfg" in options:
            also = [(57, 55), (19, 17), (76, 74), (38, 36)] if frame == 0 else []
            write_cfg(options["cfg"], *piece_lines(pieces, lambda s: "shot_dflame_%d" % s, height, GLOW_BIG, hot,
                                                   pieces[0][0], also))
    names = ["shot_dflame_%d" % s for s, _ in WALL_PIECES]
    if only is None or any(n in only for n in names):
        k.reset()
        whole = triangulate(build_wall("dflame_wall"))
        bpy.context.view_layer.update()
        height = max(v.co.z for o in whole for v in o.data.vertices)
        export_pieces(lambda s: "shot_dflame_%d" % s, whole, WALL_PIECES, options, sheets, (48, 28), "fire wall")
        if "cfg" in options:
            write_cfg(options["cfg"], *piece_lines(WALL_PIECES, lambda s: "shot_dflame_%d" % s, height, GLOW_WALL,
                                                   WALL_HOT, 10))


if __name__ == "__main__":
    build()
