"""The Plasma Storm's blast (option shapes 22, 23 and 24: 62 x 24, 65 x 28 and 62 x 23 pixels, the top, middle and
bottom of one egg of fire 65 x 75), modelled (2026-10-30, the fifth round of the shots' models: the big shots some
weapons draw blended from the option shapes; until then they went into the shots' captured layer and showed in the 3D
view as flat images of the screen's pixels, a tall flat column of pixel fire). Built with polish_shot_fireball.py's kit
and polish_shot_zflame.py's method (a low bed of fire round its hot spot, billows standing out of it, bands of ramp 7 on
the mesh's rings) and cut into its pieces as polish_shot_megacannon.py cuts its blasts.

Who fires it: the sidekick Plasma Storm (option 9, "Ammo 6", 9500, sold from the first shop on: 22 shop lists in
episodes 1-5), on its own key (Left Ctrl for the left sidekick, Left Option/Alt for the right: an ammo sidekick fires
only on its key, mainint.c): weapon 88, the same in all five episodes: multi 3, three shots made together in one tick
that the game moves together, each a piece of the blast: sg 60023 (option shape 22) at by -24, 60024 (23) at by 0,
60025 (24) at by 28, all at bx -32 (drawn from x - 31: the three share their left edge; 23 is 3 pixels wider on the
right), sx 120 (the blast's x follows the player's each tick), sy 10 (up the screen at 10 pixels a tick), attack
252/251 (250 and over: it flies on through what it hits), weapani 0 (no animation: the three shapes are pieces, not
frames), del 255. A blast every 4 ticks while the key is held (shotrepeat 3), one ammo each: six (ammo 6), then one
every (105 - 6) * 4 = 396 ticks: a stream of up to six eggs 40 pixels apart, each 75 tall (overlapping by 35), from
each sidekick that fires. blit_sprite_blend draws each shape from its top left (hue from the shape, value the average of
the screen's and the shape's: half see-through); in 3D models.cfg's "shot options" lines put each piece's model on its
shape's middle (layer3d.c l3d_add_option_shot), keyed and moving between ticks as a shot.

As the shapes draw it together (ramp 7, the fire: 0x72 dark red .. 0x77 red .. 0x7a orange .. 0x7c yellow .. 0x7e pale
yellow; the white is 0x1f, the grey ramp's white, the same colour as 0x7f; one character a pixel below: a hex digit the
shade of ramp 7, 'w' the white): an egg of white-hot plasma 62-65 wide, its white filling most of it (about 45 x 60),
its rim 6-12 pixels of turbulent fire, yellow and pale yellow licks (0x7d, 0x7e) and white flecks in orange (0x7a-0x7c),
a dark red edge (0x72-0x78); 24 is 22 upside down, so its top and bottom are alike.

The model (each blast built whole, then put into its three pieces). Its heat is the shape's idealized and cooled: the
shape's own white filling most of the egg, solid and lit, burnt the stream (six eggs overlapping, the game's bloom) into
one white slab, and in the 2D game the stream never looked white (blended at half value, it showed orange and yellow
over the ground, red over space); so the egg is a ball of fire, a pale yellow heart, yellow and orange billows, a thin
red edge.
- the bed: a low dome over the egg's outline (its pixels row by row, smoothed) round its hot spot (where the shades
  blurred over SIGMA_BED pixels are hottest), BED_HEIGHT times the egg's radius high; its heat BED_MAX in the middle
  falling (as the BED_FALL power of the way out) to the rim's heat at the outline (the shades blurred over RIM_SIGMA
  RIM_AT of the way out, at most RIM_MAX: the thin red edge), never rising outwards, in bands of ramp 7 on the mesh's
  rings (kit.Dome): the creases between the billows a band or two cooler than the billows round them.
- the billows: raised patches on the bed (kit.Dome over the bed's top, clipped to the outline), placed hottest first on
  the hottest pixels (blurred over SIGMA) that no billow covers yet, until they cover BILLOW_COVER of the egg (at most
  BILLOW_MOST times as many as would tile it); BILLOW_R0 + BILLOW_RK times the egg's radius wide, times BILLOW_SIZE by
  the way out (big lumps in the heart, small licks at the rim) and a jitter (BILLOW_JITTER, from a hash of the point);
  each billow's heat the blurred shades there under COOL's ceiling (falling from the hot spot to the rim), never rising
  outwards, its crown CROWN of the way to the hottest pixel near (at most CROWN_MAX): fire boiling.
- the bands: BANDS, ramp 7 from 0x74 (the edge) to 0x7f (its heart reaches 0x7e), emission 0.2-0.38, lower than the
  small fire shots' (0.26-0.62): the egg is 65 x 75 and the stream's eggs overlap.
- the pieces: the bed cut along the shapes' edges with open cuts (zflame.cut_open: the three are always drawn together,
  so the cuts are never seen), each billow whole in the piece that holds its middle; each piece moved so that its
  shape's middle is its origin; model lines "origin" (drawn at their own origin), shot lines height= the blast's
  height and TOP_UNDER more down: its top half a pixel under the player's layer. Centred on the layer as the other
  shots are (height= half its height down), the newest egg (24 pixels above to 51 below the sidekick's y) buried the
  player's ship (the Talon 4.2 pixels tall round the layer) and its sidekicks while firing; the 2D game draws them over
  the shapes, so now they ride on the fire (its base at about the clouds' layer, 30 over the ground). A blast is
  3 694 triangles whole, 4 033 in its pieces (22: 716, 23: 2 605, 24: 712: most billows land in the middle piece),
  5-7 materials a piece (0x74-0x7c; 23's heart 0x7d, 0x7e).
- no glow (glow=1:0 on all three: an option shot's glow= is its only glow, and 1:0 is none). One glow a blast (64
  pixels at 0.12 in 0x7b on the middle piece, GLOW) was tried: hardly seen round the bright egg, and each glow cost
  about 0.24 ms of GPU time whatever its size (36 or 64 pixels: the light it casts, not its sprite): both streams
  full (twelve blasts) 12.1 ms before, 17.0 ms with the glows, 14.0 without. The 2D shapes had no glow either; the
  egg's own emission carries it. GLOW = None; set it to put the glow back.
- fewer, bigger billows (BILLOW_R0 4, BILLOW_RK 0.25: 14 billows, 9.5-14 pixels in the heart): 29 smaller ones read
  the same at 1x and cost 0.35 ms more in the same scene (the bed alone +0.9 ms, the billows +0.6).

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera; the whole blast
built round the point (the sidekick's x - 31 + 31, its y): column c of the whole (the three shapes stacked) is
x = c + 0.5 - 31, row r is y = 23.5 - r (22's rows 0-23 above y 0, 23's rows 24-51, 24's rows 52-74), each piece
then moved onto its own shape's middle (22: 0, 12; 23: 1.5, -14; 24: 0, -39.5); built on z = 0.

models.cfg: see the block's comment; --cfg <file> appends the lines.

Run: Blender -b --factory-startup -P tools/blender/models/shots/polish_shot_plasmastorm.py -- [--only <name,...>]
     [--outdir <dir>] (default assets/models/shots) [--check <any>] (the whole's silhouette against the three shapes'
     pixels above) [--preview <prefix>] (the whole's top, three-quarter
     and game-camera views; with --pieces <any> each piece's too) [--cfg <file>]
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
from polish_shot_megacannon import polar  # noqa: E402
import polish_shot_zflame as zf  # noqa: E402

# The three shapes stacked as the game draws them (22 rows 0-23, 23 rows 24-51, 24 rows 52-74; 65 columns): a hex digit
# the shade of ramp 7, 'w' the white (0x1f), '.' transparent.
STORM = """
......................46679975556...3234656778344................
....................448aaa9999aa765788899868a874544..............
...................5459bcbbbceedc977898aba7abc9a8855.............
..................57abcecccdwwwed98acbceedbceedcd9976............
.................56ddeeddcdwweddbaacdewwweccdewedc7a7............
................98bcedcddewedcdccbccceewwwdcccdeeb7a96...........
..............78bbbccccdddcdbcedcbceecweeeedccccdc8ab97..........
.............879bcdeedbdcbccddddewwwwdddccewedcccb8aa9966........
...........79989adwwwdabddedewdbewwwwedccddwwwedcb9797bb86.......
..........57aa99dewwwcdbcewwwwwdewwwwecbccdwwwewddba88cdb85......
.........479bbbddwwecdcaewwwwwwedeeeeecdeeedeweewdcaa6adec95.....
.........789bddceeecceddwwwwwwwweeeeeedewewededdeecab87bdda7.....
........599bcdcbcccdwwdewwwwwwwwwwwwwwedewwwwedcewdcdda8cba7.....
........89accdcbdeewwweewwwwwwwwwwwwwwwedewwwwdcwwecdwdaba77.....
........99abcdcdcewwweeewwwwwwwwwwwwwwwwwewwwwdcwweccddcb96......
.......799accdedeewwweewwwwwwwwwwwwwwwwwweewwwdbwwwdccdcca8......
.......8bbdddcdeeewweewwwwwwwwwwwwwwwwwwwwewwwecceeweeeddc8......
......79bcdedcwwdeeeewwwwwwwwwwwwwwwwwwwwweewweeaddewweedc95.....
......5bcbeedewwdeeeewwwwwwwwwwwwwwwwwwwwwweewwcddeeeeddecb7.....
......6bbcwedwwweeeewwwwwwwwwwwwwwwwwwwwwwweeeecewwwweddccc98....
.....57bcewdewwwweewwwwwwwwwwwwwwwwwwwwwwwwewwwedeeeeeeaccdb87...
....89abewwdwwwwwewwwwwwwwwwwwwwwwwwwwwwwwwdewweeeeweedbceeb86...
...88bcdwweewwwwwewwwwwwwwwwwwwwwwwwwwwwwwweewweewwwwwecewwca8...
...79cedwwdewwwwwewwwwwwwwwwwwwwwwwwwwwwwwedeewewwwwwedewdec96...
...a9bcbbceewwwweeeewwwwwwwwwwwwwwwwwwwwwwwwwwwdwwwwddceeccb8....
..78babbccdewwwweedwwwwwwwwwwwwwwwwwwwwwwwwwwwwdwweedeeddba97....
.69bbbdcccewwweedddwwwwwwwwwwwwwwwwwwwwwwwwwwwwdweddeecdab88.....
.78abcwdbbcewwwdddcewwwwwwwwwwwwwwwwwwwwwwwwwwwdwedewwbaaa99.....
59898bweccceweddddeewwwwwwwwwwwwwwwwwwwwwwwwwwwdwecewebbcba9.....
4899acwecdcdwdccdewewwwwwwwwwwwwwwwwwwwwwwwwwwwdwecwweccwc976....
5678baweccccedcddwweewwwwwwwwwwwwwwwwwwwwwwwwwwddecwwebcwca845...
557a98bedcdcdcddewwwewwwwwwwwwwwwwwwwwwwwwwwwwwecwcwwdccdcb9853..
.68a879dccecdddcewwwewwwwwwwwwwwwwwwwwwwwwwwwwwedwddedcbabca974..
.69ca8acbdebdeedewwwewwwwwwwwwwwwwwwwwwwwwwwwwwedweddddbabca874..
..8ac99ccwdbdweddwwwewwwwwwwwwwwwwwwwwwwwwwwwweedwecddwcabda977..
..68aa9addcbewwedewwewwwwwwwwwwwwwwwwwwwwwwwwwcdewddcdwdaaca9a65.
..59bcaaccbbdewddewewwwwwwwwwwwwwwwwwwwwwwwwweeeeeddccddaadba984.
..6aacbabcdbddedeewewwwwwwwwwwwwwwwwwwwwwwwwweweededdbdcbabdca6..
.489abdaaddccddeeeeewwwwwwwwwwwwwwwwwwwwwwwwweweddwedbbccabwwd...
.56a9acaadwdcddwedcwwwwwwwwwwwwwwwwwwwwwwwwwewwedewwebcddaawww8..
..779adbacwddcewdeewwwwwwwwwwwwwwwwwwwwwwwwwewwwddewdbdwcc9bwe85.
..478acbabddddewdewwwwwwwwwwwwwwwwwwwwwwwwwwewwwedeedbedbca9dwa6.
..479acbabcdeddwdewwwwwwwwwwwwwwwwwwwwwwwwwwewwwecdddceccd97ad96.
..3589bcdccdwwcwcewwwwwwwwwwwwwwwwwwwwwwwwwwewwweddcdcdcdeb8ac95.
...548acwcbewwceddwwwwwwwwwwwwwwwwwwwwwwwwwweewwddcdeccccewaba975
....679cwccewwcewdwwwwwwwwwwwwwwwwwwwwwwwwwwwewedccdwdcdcewcabc94
.....9abcbbewecewdwwwwwwwwwwwwwwwwwwwwwwwwwwweeddddewecccewb9cba5
.....99aaabwwedewdwwwwwwwwwwwwwwwwwwwwwwwwwwwecdddwwwecbbdwccca7.
.....88badceeddewdwwwwwwwwwwwwwwwwwwwwwwwwwwwwdddeewwwecccdbbc96.
....79abddeedeewwdwwwwwwwwwwwwwwwwwwwwwwwwwwwwdeewwwwedccbbab87..
....8bcceecddwwwwdwwwwwwwwwwwwwwwwwwwwwwwwwwweeeewwwweecbbcb9a...
...79cedwwdewwwwwewwwwwwwwwwwwwwwwwwwwwwwwwwwwwewwwwwedwwdec97...
...88bcdwweewwwwwewwwwwwwwwwwwwwwwwwwwwwwwweewweewwwwwecewwca8...
....89abewwdwwwwwewwwwwwwwwwwwwwwwwwwwwwwwwdewweeeeweedbceeb86...
.....57bcewdewwwweewwwwwwwwwwwwwwwwwwwwwwwwewwwedeeeeeeaccdb87...
......6bbcwedwwweeeewwwwwwwwwwwwwwwwwwwwwwweeeecewwwweddccc98....
......5bcbeedewwdeeeewwwwwwwwwwwwwwwwwwwwwweewwcddeeeeddecb7.....
......79bcdedcwwdeeeewwwwwwwwwwwwwwwwwwwwweewweeaddewweedc95.....
.......8bbdddcdeeewweewwwwwwwwwwwwwwwwwwwwewwwecceeweeeddc8......
.......799accdedeewwweewwwwwwwwwwwwwwwwwweewwwdbwwwdccdcca8......
........99abcdcdcewwweeewwwwwwwwwwwwwwwwwewwwwdcwweccddcb96......
........89accdcbdeewwweewwwwwwwwwwwwwwwedewwwwdcwwecdwdaba77.....
........599bcdcbcccdwwdewwwwwwwwwwwwwwedewwwwedcewdcdda8cba7.....
.........789bddceeecceddwwwwwwwweeeeeedewewededdeecab87bdda7.....
.........479bbbddwwecdcaewwwwwwedeeeeecdeeedeweewdcaa6adec95.....
..........57aa99dewwwcdbcewwwwwdewwwwecbccdwwwewddba88cdb85......
...........79989adwwwdabddedewdbewwwwedccddwwwedcb9797bb86.......
.............879bcdeedbdcbccddddewwwwdddccewedcccb8aa9966........
..............78bbbccccdddcdbcedcbceecweeeedccccdc8ab97..........
................98bcedcddewedcdccbccceewwwdcccdeeb7a96...........
.................56ddeeddcdwweddbaacdewwweccdewedc7a7............
..................57abcecccdwwwed98acbceedbceedcd9976............
...................5459bcbbbceedc977898aba7abc9a8855.............
....................448aaa9999aa765788899868a874544..............
......................46679975556...3234656778344................
"""
WHITE = 16.0  # (the white's heat: hotter than ramp 7's 0x7e)
X0, Y0 = 31.0, 23.5  # (column c is x = c + 0.5 - X0, row r is y = Y0 - r)

# The pieces: (option shape, its box in the whole (x0, x1, y0, y1)).
PIECES = [(22, (-31.0, 31.0, 0.0, 24.0)), (23, (-31.0, 34.0, -28.0, 0.0)), (24, (-31.0, 31.0, -51.0, -28.0))]

# The fire's bands (lowest heat, palette index, emission), ramp 7 from the rim's dark red to the white of the billows'
# crowns; the heat is in the shapes' shades (0-15, the white 16).
BANDS = [(-99.0, 0x74, 0.2), (5.5, 0x76, 0.24), (6.9, 0x78, 0.28), (8.2, 0x7a, 0.32), (9.4, 0x7b, 0.34),
         (10.6, 0x7c, 0.35), (11.8, 0x7d, 0.36), (12.9, 0x7e, 0.37), (14.4, 0x7f, 0.38)]

# The bed: its height over the egg's radius and the power of its profile; its heat (the shades blurred over SIGMA_BED):
# in its middle their mean over the inner half (at most BED_MAX), falling to the blurred shades near the outline as the
# BED_FALL power of the way out; the waves of its bands' borders.
BED_HEIGHT, BED_POWER = 0.26, 0.6
SIGMA_BED, BED_MAX, BED_FALL = 2.5, 12.4, 1.6
BED_TONGUES = (9, 0.025, 1.3)
RIM_AT, RIM_SIGMA, RIM_MAX = 0.96, 1.2, 7.5
# The billows: their radius (BILLOW_R0 + BILLOW_RK * the egg's radius), how far they stand out of the bed (times their
# radius), how much of the egg they cover before the placing stops, how far their middles stay apart (times their
# radii's sum); their heat the shades blurred over SIGMA, their crowns CROWN of the way to the hottest pixel near.
BILLOW_R0, BILLOW_RK = 4.0, 0.25
BILLOW_LIFT = 0.3
BILLOW_COVER = 0.95
BILLOW_MOST = 1.9  # (at most this many times as many billows as would tile the egg)
BILLOW_APART = 0.55
SIGMA = 1.6
CROWN, CROWN_MAX = 0.25, 15.5
# The billows' size (times their radius) from the hot spot (u 0) to the rim (u 1), and its jitter (a fraction, +-).
BILLOW_SIZE = ((0.0, 1.35), (0.5, 1.1), (1.0, 0.65))
BILLOW_JITTER = 0.15
# The billows' heat's ceiling from the hot spot (u 0) to the rim (u 1).
COOL = ((0.0, 13.6), (0.15, 13.0), (0.3, 11.9), (0.5, 10.7), (0.7, 9.5), (0.88, 8.3), (1.0, 7.2))

# How far under the player's layer the blast's top lies (height= -(its height + TOP_UNDER)): the player's ship and
# sidekicks ride on the fire.
TOP_UNDER = 0.5

# The glow (glow=), one a blast, on its middle piece: size, strength, colour (dx, dy: the hot spot's, from the piece's
# middle); None: no glow (see the docstring: each glow's light costs about 0.24 ms).
GLOW = None


def shades():
    """The whole's pixels: an array of shades (rows from the top, 75 x 65), the white WHITE, nan where transparent."""
    rows = STORM.strip("\n").splitlines()
    return np.array([[np.nan if ch == "." else WHITE if ch == "w" else float(int(ch, 16)) for ch in r] for r in rows])


def pixel_xy(r, c):
    return c + 0.5 - X0, Y0 - r


def outline(S):
    """The whole's outline (its pixels' edges row by row), smoothed: a closed polygon."""
    rows = []
    for r in range(S.shape[0]):
        cols = np.where(~np.isnan(S[r]))[0]
        if len(cols):
            rows.append((r, int(cols[0]), int(cols[-1])))
    right = [(c1 + 1 - X0, Y0 - r) for r, _, c1 in rows]
    left = [(c0 - X0, Y0 - r) for r, c0, _ in rows]
    (r0, a0, b0), (r1, a1, b1) = rows[0], rows[-1]
    points = [((a0 + b0 + 1) / 2 - X0, Y0 + 0.5 - r0)] + right + [((a1 + b1 + 1) / 2 - X0, Y0 - 0.5 - r1)] + left[::-1]
    return mk.chaikin(points, iterations=3)


def sample(field, x, y):
    """The field (rows from the top) at a point, bilinear; outside the shapes the nearest pixel's."""
    c, r = x + X0 - 0.5, Y0 - y
    c0, r0 = int(math.floor(c)), int(math.floor(r))
    total, weight = 0.0, 0.0
    for dr in (0, 1):
        for dc in (0, 1):
            rr, cc = r0 + dr, c0 + dc
            if 0 <= rr < field.shape[0] and 0 <= cc < field.shape[1] and not np.isnan(field[rr, cc]):
                w = (1 - abs(r - rr)) * (1 - abs(c - cc))
                total += w * field[rr, cc]
                weight += w
    if weight > 1e-6:
        return total / weight
    rr, cc = np.where(~np.isnan(field))
    i = int(np.argmin((rr - r) ** 2 + (cc - c) ** 2))
    return float(field[rr[i], cc[i]])


class Blast:
    """The whole blast: its outline, heat, size, bed and billows (zflame.Frame's, for the three shapes stacked)."""

    def __init__(self):
        self.S = shades()
        self.F = zf.smoothed(self.S, SIGMA)
        self.C = zf.smoothed(self.S, SIGMA_BED)
        self.poly = outline(self.S)
        rr, cc = np.where(~np.isnan(self.S))
        self.pixels = [pixel_xy(r, c) + (self.S[r, c],) for r, c in zip(rr, cc)]
        self.area = float(len(self.pixels))
        self.radius = math.sqrt(self.area / math.pi)
        top = float(np.nanmax(self.C))
        hot = [(x, y, sample(self.C, x, y)) for x, y, _ in self.pixels]
        hot = [(x, y, h - (top - 0.8)) for x, y, h in hot if h > top - 0.8]
        total = sum(w for _, _, w in hot)
        self.hot = (sum(x * w for x, _, w in hot) / total, sum(y * w for _, y, w in hot) / total)
        self.bed_radius = polar(self.poly, self.hot, samples=360)
        self.bed_height = BED_HEIGHT * self.radius

        inner = [sample(self.C, x, y) for x, y, _ in self.pixels
                 if math.hypot(x - self.hot[0], y - self.hot[1]) < 0.5 * self.bed_radius(math.atan2(y - self.hot[1],
                                                                                                      x - self.hot[0]))]
        middle = min(BED_MAX, float(np.mean(inner)) + 0.5)
        # the rim's heat round the egg: the shades (blurred over RIM_SIGMA) RIM_AT of the way out, smoothed round, at
        # most RIM_MAX (the egg's thin orange and red edge)
        edge = zf.smoothed(self.S, RIM_SIGMA)
        rims = []
        for j in range(72):
            phi = 2 * math.pi * j / 72
            d = RIM_AT * self.bed_radius(phi)
            rims.append(sample(edge, self.hot[0] + d * math.cos(phi), self.hot[1] + d * math.sin(phi)))
        rims = [min(RIM_MAX, middle - 0.3, sum(rims[(j + i) % 72] for i in range(-3, 4)) / 7) for j in range(72)]
        self.middle = middle

        def bed_profile(phi, u):
            a = (phi % (2 * math.pi)) / (2 * math.pi) * 72
            i, t = int(a) % 72, a - int(a)
            rim = rims[i] * (1 - t) + rims[(i + 1) % 72] * t
            return middle - (middle - rim) * min(max(u, 0.0), 1.0) ** BED_FALL
        self.bed_heat = zf.RayHeat(bed_profile, rays=144, steps=60)
        # the billows' heat: the shades blurred over SIGMA, under a ceiling falling from the hot spot to the rim (COOL:
        # white in the heart, pale yellow, yellow, orange towards the rim), so that the egg is a ball of fire, not a
        # white slab
        ceiling = kit.curve(COOL)
        F = self.F.copy()
        for r in range(F.shape[0]):
            for c in range(F.shape[1]):
                if not np.isnan(F[r, c]):
                    x, y = pixel_xy(r, c)
                    dx, dy = x - self.hot[0], y - self.hot[1]
                    u = math.hypot(dx, dy) / max(self.bed_radius(math.atan2(dy, dx)), 1e-6)
                    F[r, c] = min(F[r, c], ceiling(min(u, 1.0)))
        self.F = F
        self.billows = self.place_billows()

    def bed_heat_xy(self, x, y):
        dx, dy = x - self.hot[0], y - self.hot[1]
        phi = math.atan2(dy, dx)
        return self.bed_heat(math.hypot(dx, dy) / max(self.bed_radius(phi), 1e-6), phi)

    def bed_top(self, x, y):
        dx, dy = x - self.hot[0], y - self.hot[1]
        r = math.hypot(dx, dy)
        if r < 1e-9:
            return self.bed_height
        rho = r / self.bed_radius(math.atan2(dy, dx))
        return self.bed_height * max(0.0, 1.0 - rho * rho) ** BED_POWER

    def billow_radius(self, x, y, r0):
        """A billow's radius at a point: r0 times BILLOW_SIZE by the way out from the hot spot (big lumps in the heart,
        small licks at the rim), times a jitter of +-BILLOW_JITTER from a hash of the point (the same every build)."""
        dx, dy = x - self.hot[0], y - self.hot[1]
        u = min(math.hypot(dx, dy) / max(self.bed_radius(math.atan2(dy, dx)), 1e-6), 1.0)
        h = math.sin(x * 12.9898 + y * 78.233) * 43758.5453
        return r0 * self.size(u) * (1.0 + BILLOW_JITTER * (2.0 * (h - math.floor(h)) - 1.0))

    def place_billows(self):
        """Billows, hottest first: each on the hottest pixel (blurred) no billow covers yet (its middle further from
        each billow's than BILLOW_APART times their radii's sum), until they cover BILLOW_COVER of the egg or there are
        as many as its size allows: (x, y, radius, crown heat)."""
        r0 = BILLOW_R0 + BILLOW_RK * self.radius
        self.size = kit.curve(BILLOW_SIZE)
        most = max(2, int(round(self.area / (math.pi * r0 * r0) * BILLOW_MOST)))
        points = [(x, y, sample(self.F, x, y), self.billow_radius(x, y, r0)) for x, y, _ in self.pixels]
        billows = []
        while len(billows) < most:
            free = [p for p in points if all(math.hypot(p[0] - b[0], p[1] - b[1]) > BILLOW_APART * (b[2] + p[3])
                                             for b in billows)]
            if not free:
                break
            x, y, h, r = max(free, key=lambda p: (p[2], -p[0], p[1]))
            near = max(s for px, py, s in self.pixels if math.hypot(px - x, py - y) < 0.6 * r)
            crown = max(h + 0.6, h + CROWN * (min(near, CROWN_MAX) - h))
            billows.append((x, y, r, crown))
            covered = sum(1 for px, py, _ in self.pixels
                          if any(math.hypot(px - b[0], py - b[1]) < 0.8 * b[2] for b in billows))
            if covered >= BILLOW_COVER * self.area:
                break
        return billows


def build_bed(name, bl, mats):
    dome = kit.Dome(bl.hot, bl.bed_radius, bl.bed_top, bl.bed_heat, BANDS, segments=60, tongues=BED_TONGUES, gap=0.2,
                    middle_fractions=(0.3, 0.6), rim_fractions=(0.4, 0.7, 0.88, 1.0))
    return dome.build(name, mats)


def build_billow(name, bl, billow, mats):
    """A billow: a raised patch on the bed (round its middle, clipped to the outline); its heat the shades' (blurred,
    never rising outwards from its middle), its crown hotter, its rim as hot as the bed there."""
    bx, by, r, crown = billow
    clip = polar(bl.poly, (bx, by), samples=180)
    lift = BILLOW_LIFT * r

    def radius(phi):
        return min(r * (1.0 + 0.08 * math.sin(phi)), 0.94 * clip(phi))

    def top(x, y):
        dx, dy = x - bx, y - by
        d = math.hypot(dx, dy)
        rho = d / max(radius(math.atan2(dy, dx)), 1e-6) if d > 1e-9 else 0.0
        return bl.bed_top(x, y) + lift * max(0.0, 1.0 - rho * rho) ** 0.5
    centre = sample(bl.F, bx, by)

    def profile(phi, u):
        x, y = bx + u * radius(phi) * math.cos(phi), by + u * radius(phi) * math.sin(phi)
        own = sample(bl.F, x, y) + (crown - centre) * (1.0 - u) ** 1.5
        w = mk.smoothstep(0.6, 1.0, u)
        return own * (1 - w) + bl.bed_heat_xy(x, y) * w
    heat = zf.RayHeat(profile, rays=48, steps=30)
    segs = 12 if r >= 5.0 else 10
    dome = kit.Dome((bx, by), radius, top, heat, BANDS, segments=segs, tongues=(3, 0.04, 1.0), gap=0.3,
                    middle_fractions=(0.45,), rim_fractions=(0.55, 1.0))
    return dome.build(name, mats)


def build_whole():
    """The blast whole: (Blast, bed, [billows])."""
    bl = Blast()
    mats = kit.materials("plasmastorm_fire", BANDS)
    bed = zf.prune(build_bed("plasmastorm_bed", bl, mats))
    billows = [zf.prune(build_billow("plasmastorm_billow%d" % i, bl, b, mats)) for i, b in enumerate(bl.billows)]
    return bl, bed, billows


def piece_of(x, y):
    """The piece (its shape) whose box holds the point."""
    for shape, (x0, x1, y0, y1) in PIECES:
        if x0 <= x < x1 and y0 <= y < y1:
            return shape
    return min(PIECES, key=lambda p: math.hypot(x - (p[1][0] + p[1][1]) / 2, y - (p[1][2] + p[1][3]) / 2))[0]


def centre_of(box):
    return (box[0] + box[1]) / 2, (box[2] + box[3]) / 2


def pieces(bl, bed, billows):
    """The blast in its three shapes' pieces, each moved onto its shape's middle: {shape: [objects]}."""
    out = {}
    for shape, box in PIECES:
        cx, cy = centre_of(box)
        parts = []
        piece = zf.cut_open(bed, box)
        if piece is not None:
            piece.name = "%s_o%d" % (bed.name, shape)
            parts.append(piece)
        for obj, b in zip(billows, bl.billows):
            if piece_of(b[0], b[1]) == shape:
                copy = obj.copy()
                copy.data = obj.data.copy()
                bpy.context.scene.collection.objects.link(copy)
                copy.name = "%s_o%d" % (obj.name, shape)
                parts.append(copy)
        for p in parts:
            p.data.transform(Matrix.Translation((-cx, -cy, 0.0)))
        out[shape] = parts
    return out


def cfg_lines(bl, height):
    """The models.cfg lines: [model lines], [shot lines]."""
    models, shots = [], []
    what = {22: "the blast's top (one blast in three)", 23: "its middle", 24: "its bottom"}
    for shape, box in PIECES:
        name = "shot_plasmastorm_%d" % shape
        models.append("model %-20s shots/%s.glb origin" % (name, name))
        cx, cy = centre_of(box)
        if shape == 23 and GLOW is not None:
            size, strength, colour = GLOW
            glow = "glow=%d:%.2f:%d:%.2f:%.2f" % (size, strength, colour, bl.hot[0] - cx, cy - bl.hot[1])
        else:
            glow = "glow=1:0"
        shots.append("shot options %d %-20s height=%.2f %-30s # %s" % (shape, name, -(height + TOP_UNDER), glow,
                                                                        what[shape]))
    return models, shots


def build():
    options = k.args()
    only = set(options["only"].split(",")) if "only" in options else None
    outdir = options.get("outdir", kit.OUTDIR)
    sheets = options.get("check")
    k.reset()
    bl, bed, billows = build_whole()
    whole = triangulate([bed] + billows)
    bpy.context.view_layer.update()
    height = max(v.co.z for o in whole for v in o.data.vertices)
    print("== the blast whole: radius %.2f, hot spot %.2f %.2f, bed middle %.2f, %d billows %s; %d triangles, "
          "height %.2f" % (bl.radius, bl.hot[0], bl.hot[1], bl.middle, len(bl.billows),
                           " ".join("(%.1f %.1f r%.1f h%.1f)" % b for b in bl.billows), mk.triangles(whole), height))
    if "cfg" in options:
        models, shots = cfg_lines(bl, height)
        with open(options["cfg"], "a") as out:
            out.write("\n".join(models + shots) + "\n")
    if sheets:
        mask = [[bool(np.isfinite(v)) for v in row] for row in bl.S]
        mk.compare("the blast whole (option shapes 22 23 24)", mk.coverage(whole, 65, 75, centre=(1.5, -13.5)), mask)
    if "preview" in options:
        # (copies moved onto the egg's middle for the views: moving the whole there and back would change its points'
        # last bits, and the GLBs must be the same with or without --preview)
        bpy.context.scene.view_settings.view_transform = "Standard"
        copies = []
        for o in whole:
            c = o.copy()
            c.data = o.data.copy()
            bpy.context.scene.collection.objects.link(c)
            c.data.transform(Matrix.Translation((-1.5, 13.5, 0.0)))
            copies.append(c)
        view(options["preview"] + "plasmastorm_whole", copies, size=(65, 75))
        for c in copies:
            mesh = c.data
            bpy.data.objects.remove(c)
            bpy.data.meshes.remove(mesh)
    cut = pieces(bl, whole[0], whole[1:])
    for o in whole + [o for parts in cut.values() for o in parts]:
        o.hide_render = True
    for shape, parts in cut.items():
        name = "shot_plasmastorm_%d" % shape
        if only is not None and name not in only:
            continue
        for o in parts:
            o.hide_render = False
        bpy.context.scene.view_settings.view_transform = "Standard"
        bpy.context.view_layer.update()
        mk.report(name, parts, os.path.join(outdir, name + ".glb"))
        if "preview" in options and "pieces" in options:
            view(options["preview"] + name, parts, size=(65, 28))
        for o in parts:
            o.hide_render = True


if __name__ == "__main__":
    build()
