"""The wall of fire that sweeps down FLEET and LAVA RUN (sheet K, 2x2 sprites, 24 x 28 pixels, one frame each;
indestructible), polished (2026-10-20; it replaces wave3_o.py's fire_whole() and fire_piece(), a pillow lofted
through the sprites' outline and painted with their pixels, which read as blocks). models.cfg: model fire_head_l /
fire_head_c / fire_head_r / fire_mid_l ... fire_tail_r ... origin; sprite k 89 fire_head_l yaw=0 glow=30:0.12 and so
on.

The game builds the wall from a row of three head sprites (K 89, 91, 93), rows of the three middle sprites (K 51, 53,
55) and a row of the three tail sprites (K 13, 15, 17), 72 pixels wide, all moving down the screen together (enemies
713-721, ymove 4). FLEET's events (2640-2652 and on, sky layer) put the head at the bottom, four middle rows above it
and the tail on top, every 24 pixels (the sprites are 28 high: the rows overlap by 4); LAVA RUN's (2040-2050, on the
ground layer, carried by its scroll) put the fourth middle row 28 pixels above the third and the tail 20 above it.
The head sprites are the tail's upside down (K 89's row r is K 13's row 26 - r). One frame each: one model a piece.

As the sprites and their 4x upscales draw it: a long rounded column of fire, white-hot all down its middle (the
fire ramp 7's 7f), yellow and orange flame tongues streaking along its sides (7b-7e, 78-7a) and a ragged dark red rim
(73-77), its ends rounded, the tail's top and the head's bottom ending in two flame tips (the gap at columns 39-41 of
the 72).

The model: a billowing mass of fire rushing down the screen. A low bed of embers covers the sprites' outline,
glowing orange in the creases; on it lie flame lobes like overlapping scales, each a billow rounded at its front
(down the screen) that tapers back up the screen into a tongue whose tip lifts and curls over (the flames swept back
as the wall rushes down), its edges rippling: white-hot along the crest down the middle, where a layer of taller
flames rises from the billows, yellow, orange and red towards the sides; every lobe hottest on its front and its top,
its flanks a few shades cooler, its tongue cooling to orange and red at the tip, and all of it cooler where it meets
the layer (the base deep red). Along each side a column of low tongues leans out over the rim, their tips flicking
out; the head's front is a row of billows rising from the layer, their fronts cooler; the tail ends in tongues
trailing off its back, the two biggest making the sprites' two tips. The heat is cut into bands of the fire ramp's
own palette indices (smooth contours, polish_orb_red.band_split), each glowing in its own colour, more the hotter
(as polish_flame_drop.py's).

The pieces: the bed is built whole and cut along the sprites' edges (polish_arch.cut, the cuts capped in the embers'
orange, the normals the whole's), each piece keeping its sprite's whole box, 24 x 28: over y -14 .. 14 the bed
repeats every 24 pixels exactly (the outline, its rings and its heat), so drawn 24 apart the overlapping 4 pixels of
two pieces are the same surface, 28 apart (LAVA RUN) they still touch. The lobes are not cut: each belongs, whole, to
the piece whose 24 x 24 cell holds its front, so drawn together every lobe is there once and a piece alone is a clump
of flames on a low slab of embers, not a block. The middle row's lobes are bent on the middle sprites' repeating
outline alone (the same whatever row comes above), and those along its sides end within 15 pixels of the row's
centre, where the tail's outline has hardly begun to narrow: what a middle piece's lobes reach into the row above
fits under a middle row and under the tail alike. The head's and the tail's lobes (the middle row's repeated, cut
short or left out towards the ends, and their own front row and trailing tongues) are bent on the whole outline.

The whole is designed straight (the column's sides at s = +-W0) and bent to the sprites' outline: a point at (s, y, z)
goes to x = c(y) + s / W0 * w(y), where c and w are the outline's middle and half-width at y (the sprites' edges row by
row: the middle sprites' rows 2-25 repeating, the tail's above y 14 and the head's below -14, blended over 3 pixels).

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up from the layer (the wall stands on
z = 0, its flames reach about 15 up: on the sky layer, 22, they stay under the player's 44); the whole's origin is the
middle row's centre (the middle sprites' pixel 12, 14), the head row's centre at y = -24, the tail's at +24, the
columns' at x = -24, 0, 24. Each piece's origin is its sprite's centre.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (each piece's silhouette
against enemy_K.png), --preview <prefix> (the whole's and each piece's top and 3/4 views), --only <name,...>,
--whole <file.glb> (also exports the whole, for looking at it).
"""
import math
import os
import random
import sys

import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k, smoothstep  # noqa: E402
from polish_arch import cut  # noqa: E402
from polish_orb_red import band_split  # noqa: E402

PITCH = 24.0  # the game's rows are 24 pixels apart
# The rows and columns: (name, sprites left to right, the row's centre y in the whole), (name, the column's centre x).
ROWS = [("tail", (13, 15, 17), 24.0), ("mid", (51, 53, 55), 0.0), ("head", (89, 91, 93), -24.0)]
COLUMNS = [("l", -24.0), ("c", 0.0), ("r", 24.0)]
PIECES = [("fire_%s_%s" % (row, col), sprites[i], (cx, cy)) for row, sprites, cy in ROWS
          for i, (col, cx) in enumerate(COLUMNS)]
PERIODIC = 14.0  # |y| up to which the whole repeats every PITCH (the middle piece's box)
BLEND = 3.0      # over how many pixels beyond it the outline turns into the head's or the tail's

# --- The sprites' outline -----------------------------------------------------------------------------------------

# Each row's first column and the column after its last, in the 72 pixels of a row of three sprites (x = column - 36).
TAIL_EDGES = [(28, 55), (26, 57), (25, 58), (24, 59), (23, 59), (22, 60), (20, 61), (19, 63), (17, 64), (16, 65),
              (15, 66), (15, 66), (14, 66), (14, 66), (14, 65), (13, 65), (13, 65), (12, 66), (12, 66), (12, 67),
              (11, 68), (10, 68), (9, 68), (9, 68)]                     # K 13-17 rows 4-27 (y = 37.5 - row)
MID_EDGES = [(9, 67), (8, 67), (7, 66), (7, 66), (6, 66), (6, 67), (6, 68), (6, 69), (7, 69), (7, 69), (8, 69),
             (8, 70), (8, 70), (8, 69), (7, 68), (7, 69), (8, 70), (8, 70), (8, 70), (8, 70), (9, 71), (10, 71),
             (11, 71), (11, 70), (11, 70), (10, 69), (10, 68), (9, 68)]  # K 51-55 rows 0-27 (y = 13.5 - row)
Y_TOP, Y_BOTTOM = 34.0, -33.0   # the tail's first row's top edge, the head's last row's bottom edge


def phase(y):
    """y within the middle's period, -12 .. 12."""
    return ((y + 12.0) % PITCH) - 12.0


class Outline:
    """The column's left and right edges at y: the middle sprites' rows 2-25 repeating every 24 pixels, the tail's
    rows above y 14 and the head's (the tail's upside down) below -14, blended in over 3 pixels; each smoothed along
    y (a Gaussian over +-2 pixels) before blending, so the middle stays exactly periodic."""

    SMOOTH = [(d * 0.5, math.exp(-(d * 0.5) ** 2 / (2 * 1.1 ** 2))) for d in range(-4, 5)]

    def __init__(self):
        self.mid = [MID_EDGES[r] for r in range(2, 26)]  # rows 2-25: y 11.5 ... -11.5
        self.cache = {}

    @staticmethod
    def _lerp(table, f, wrap):
        n = len(table)
        f0 = math.floor(f)
        t = f - f0
        i0, i1 = (f0 % n, (f0 + 1) % n) if wrap else (min(max(f0, 0), n - 1), min(max(f0 + 1, 0), n - 1))
        a, b = table[i0], table[i1]
        return (a[0] + (b[0] - a[0]) * t - 36.0, a[1] + (b[1] - a[1]) * t - 36.0)

    def raw_mid(self, y):
        return self._lerp(self.mid, (11.5 - y) % PITCH, True)

    def raw_tail(self, y):
        return self._lerp(TAIL_EDGES, min(max(37.5 - y, 4.0), 27.0) - 4.0, False)

    def raw_head(self, y):
        h = min(max(-10.5 - y, 0.0), 22.0)        # the head's row
        return self._lerp(TAIL_EDGES, 22.0 - h, False)

    def _smoothed(self, fn, y):
        total = sum(w for _, w in self.SMOOTH)
        left = sum(w * fn(y + d)[0] for d, w in self.SMOOTH) / total
        right = sum(w * fn(y + d)[1] for d, w in self.SMOOTH) / total
        return left, right

    def edges(self, y, periodic=False):
        """The edges at y; periodic: the middle's alone (as under any number of middle rows)."""
        key = (round(y, 6), periodic)
        if key not in self.cache:
            m = self._smoothed(self.raw_mid, phase(y))
            if periodic or abs(y) <= PERIODIC:
                self.cache[key] = m
            else:
                c = self._smoothed(self.raw_tail if y > 0 else self.raw_head, y)
                wt = smoothstep(PERIODIC, PERIODIC + BLEND, abs(y))
                self.cache[key] = (m[0] * (1 - wt) + c[0] * wt, m[1] * (1 - wt) + c[1] * wt)
        return self.cache[key]

    def frame(self, y, periodic=False):
        """The middle and the half-width at y."""
        left, right = self.edges(y, periodic)
        return (left + right) / 2, (right - left) / 2


OUTLINE = Outline()
W0 = 30.0  # the straight column's half-width


def bend(co, periodic=False):
    """A point of the straight column (s, y, z) on the sprites' outline."""
    c, w = OUTLINE.frame(co[1], periodic)
    return Vector((c + co[0] / W0 * w, co[1], co[2]))


# --- Heat and materials -------------------------------------------------------------------------------------------

# The heat bands: (lowest heat, palette index, emission strength in the palette colour); heat as the sprites' shades
# (0-15 of the fire ramp, 7), the hotter the more it glows. Kept well under 1: the game's bloom and the pieces'
# glow brighten it further, and stronger bands (up to 2.2) burnt the flames into one white blob in LAVA RUN.
BANDS = [(-99.0, 0x72, 0.1), (3.5, 0x74, 0.14), (5.0, 0x75, 0.17), (6.0, 0x76, 0.2), (7.0, 0x77, 0.24),
         (8.0, 0x78, 0.28), (9.0, 0x79, 0.32), (10.0, 0x7a, 0.36), (11.0, 0x7b, 0.4), (12.0, 0x7c, 0.45),
         (13.0, 0x7d, 0.5), (14.0, 0x7e, 0.56), (14.8, 0x7f, 0.65)]
CAP = 0x78  # the bed's cuts (the embers inside)
BASE_COOL = 5.0     # how much cooler the fire is where it meets the layer (its base, deep red)


def materials():
    """The bands' materials: (lowest heat, material). Fire has no gloss to speak of."""
    pal = k.level_palette()
    return [(lowest, k.material("fire_wall_%02x" % index, palette=index, metallic=0.0,
                                roughness=0.75 if index < 0x78 else 0.55, emission=pal[index], emission_strength=glow))
            for lowest, index, glow in BANDS]


def base_cooling(z):
    return BASE_COOL * (1 - smoothstep(0.0, 6.0, z)) ** 1.3


def core_heat(u):
    """The heat across the column (u: -1 at the left edge, 1 at the right): white-hot down the middle, falling
    off to red over the outer fifth."""
    return 15.8 - 8.6 * abs(u) ** 2.4


# --- The bed ------------------------------------------------------------------------------------------------------

BED_STEP = 2.0 / 3.0    # the rings' spacing (the period and the middle piece's box hold whole numbers of them)
BED_HEIGHT = 3.8        # the bed's crest
BED_ACROSS = 24         # points across its top
BED_ENDS = (Y_BOTTOM + 1.6, Y_TOP - 1.4)  # the bed stops short of the column's ends: the lobes make them


def bed_z(u, y=0.0):
    """The bed's top: a low dome across, rounded down at its ends."""
    end = smoothstep(BED_ENDS[1], BED_ENDS[1] - 3.0, y) * smoothstep(BED_ENDS[0], BED_ENDS[0] + 3.0, y)
    return BED_HEIGHT * (1 - abs(u) ** 2.6) ** 0.5 * (0.1 + 0.9 * math.sqrt(end))


def bed_heat(u, y):
    """The bed's heat: the embers' orange glowing in the creases between the lobes, yellower under the crest,
    cooler towards the column's ends; its rim (where it meets the layer) is cooled further by base_cooling."""
    end = smoothstep(BED_ENDS[1], BED_ENDS[1] - 4.0, y) * smoothstep(BED_ENDS[0], BED_ENDS[0] + 4.0, y)
    return 9.0 + 2.6 * (1 - u * u) - 3.0 * (1 - end)


def build_bed(bands):
    """The glowing bed under the lobes, over the whole outline (its rim the sprites' dark red edge); its rings lie
    every BED_STEP from y = -14, so they repeat with the middle."""
    ys = []
    y = -PERIODIC
    while y - BED_STEP > BED_ENDS[0]:
        y -= BED_STEP
    while y < BED_ENDS[1] - 0.1:
        ys.append(y)
        y += BED_STEP
    ys = [BED_ENDS[0] + 0.05] + ys + [BED_ENDS[1]]
    us = [math.sin(math.pi / 2 * (-1 + 2 * i / (BED_ACROSS - 1))) for i in range(BED_ACROSS)]
    rings, values = [], []
    for y in ys:
        for u in us:
            z = bed_z(u, y)
            rings.append(Vector((u * W0, y, z)))
            values.append(bed_heat(u, y) - base_cooling(z))
        for i in range(1, 3):  # the underside, flat
            rings.append(Vector((W0 * (1 - 2 * i / 3), y, -0.3)))
            values.append(0.0)
    n = BED_ACROSS + 2
    obj = k.loft("bed", [rings[i:i + n] for i in range(0, len(rings), n)], None,
                 start_point=(0.0, ys[0] - 0.05, 0.0), end_point=(0.0, ys[-1] + 0.05, 0.0))
    values += [5.0, 5.0]
    for v in obj.data.vertices:
        v.co = bend(v.co)
    band_split(obj, values, bands)
    return k.smooth(obj, 60)


# --- The flame lobes ----------------------------------------------------------------------------------------------

class Lobe:
    """A flame lobe: its front (s, y) in the straight column, its length back up the screen, half-width, thickness
    (times the half-width), the height its front sits at (base), how far its centre rises towards the tip (lift),
    how far its tip bends across (curl) and its S-wobble, its heat (the hottest, on its front and top) and how much
    its tongue cools towards the tip; hook and droop curl the tip over sideways and down, front is the share of its
    length its rounded front takes, wave ripples its edges, front_cool cools its front, flank its flanks."""

    def __init__(self, s, y, length, width, thick, base, lift, curl, wobble, heat, cool, hook=0.0, droop=0.0,
                 front=0.24, wave=0.0, wave_phase=0.0, front_cool=0.0, flank=3.0):
        self.s, self.y, self.length, self.width, self.thick = s, y, length, width, thick
        self.base, self.lift, self.curl, self.wobble, self.heat, self.cool = base, lift, curl, wobble, heat, cool
        self.hook, self.droop, self.front, self.wave, self.wave_phase = hook, droop, front, wave, wave_phase
        self.front_cool, self.flank = front_cool, flank

    def moved(self, dy, length=None):
        copy = Lobe(self.s, self.y, self.length, self.width, self.thick, self.base, self.lift, self.curl,
                    self.wobble, self.heat, self.cool, self.hook, self.droop, self.front, self.wave, self.wave_phase,
                    self.front_cool, self.flank)
        copy.y += dy
        if length is not None:
            copy.length = length
        return copy


def scatter(rnd, count, s_range, spacing, stretch=1.6, avoid=(), tries=6000):
    """Points (s, y) in a band of the straight column that repeats every PITCH (y in -12 .. 12), at least `spacing`
    apart from each other and from `avoid` (y distances divided by stretch: the lobes are long), the distance taken
    across the period's ends."""
    points = []
    for _ in range(tries):
        if len(points) >= count:
            break
        s = rnd.uniform(*s_range)
        y = rnd.uniform(-PITCH / 2, PITCH / 2)
        ok = True
        for ps, py in list(points) + list(avoid):
            dy = abs(y - py)
            dy = min(dy, PITCH - dy) / stretch
            if (s - ps) ** 2 + dy * dy < spacing * spacing:
                ok = False
                break
        if ok:
            points.append((s, y))
    return points


SIDE_REACH, CORE_REACH = 15.0, 26.0  # how far above its row's centre a middle lobe may reach: at the sides, inside


def periodic_lobes():
    """The middle row's lobes (fronts within y -12 .. 12 of its centre), seeded: along each side a column of low
    tongues leaning out over the rim (their tips flicking out and curling), inside it a column of broad flank
    billows between them, broad billows scattered over the crest and a layer of smaller, hotter, taller flames on
    them down the middle. Those at the sides end by SIDE_REACH, the others by CORE_REACH."""
    rnd = random.Random(2024)
    lobes = []
    taken = []

    def reach(y, length, side):
        return min(length, (SIDE_REACH if side else CORE_REACH) - y)

    for side in (-1, 1):
        start = -12.0 if side < 0 else -10.0
        for i in range(3):
            # The edge: low, red-orange tongues hooking outwards.
            y = start + 8.0 * i + rnd.uniform(0.0, 1.2)
            width = rnd.uniform(4.2, 5.0)
            s = side * (W0 - width * 0.6 - rnd.uniform(0.0, 0.6))
            taken.append((s, y))
            lobes.append(Lobe(s, y, reach(y, rnd.uniform(11.0, 13.0), True), width, rnd.uniform(0.8, 0.95),
                              bed_z(0.9) - 0.8, rnd.uniform(2.5, 3.5), side * rnd.uniform(1.2, 2.0),
                              side * rnd.uniform(0.0, 0.8), core_heat(0.88) + rnd.uniform(-0.4, 0.4),
                              rnd.uniform(3.5, 4.5), hook=side * rnd.uniform(1.4, 2.4), droop=rnd.uniform(0.8, 1.4),
                              wave=rnd.uniform(0.08, 0.16), wave_phase=rnd.uniform(0, 2 * math.pi)))
            # The flank, between the edge's tongues: broad orange-yellow billows.
            y = start + 4.0 + 8.0 * i + rnd.uniform(-0.8, 0.8)
            u = side * rnd.uniform(0.58, 0.66)
            width = rnd.uniform(5.0, 6.0)
            taken.append((u * W0, y))
            lobes.append(Lobe(u * W0, y, reach(y, rnd.uniform(13.0, 16.0), True), width, rnd.uniform(0.8, 0.92),
                              bed_z(u) - 1.4, rnd.uniform(3.5, 4.8), side * rnd.uniform(0.6, 1.6),
                              rnd.uniform(-0.8, 0.8), core_heat(u) - 0.5 + rnd.uniform(-0.4, 0.4),
                              rnd.uniform(4.5, 5.5), hook=rnd.choice((-1, 1)) * rnd.uniform(0.8, 1.6),
                              droop=rnd.uniform(0.8, 1.6), front=0.3, wave=rnd.uniform(0.06, 0.14),
                              wave_phase=rnd.uniform(0, 2 * math.pi)))
    for s, y in scatter(rnd, 9, (-0.42 * W0, 0.42 * W0), 6.6, avoid=taken):
        u = s / W0
        width = rnd.uniform(5.0, 7.0)
        lobes.append(Lobe(s, y, reach(y, rnd.uniform(13.0, 18.0), False), width, rnd.uniform(0.82, 0.95),
                          bed_z(u) - 1.6, rnd.uniform(4.5, 6.0), rnd.uniform(-1.0, 1.0), rnd.uniform(-1.0, 1.0),
                          core_heat(u) - 0.5 + rnd.uniform(-0.4, 0.4), rnd.uniform(4.0, 5.2),
                          hook=rnd.choice((-1, 1)) * rnd.uniform(0.8, 1.8), droop=rnd.uniform(0.8, 1.8), front=0.3,
                          wave=rnd.uniform(0.06, 0.14), wave_phase=rnd.uniform(0, 2 * math.pi),
                          flank=2.0 + 2.2 * abs(u)))
    for s, y in scatter(rnd, 6, (-0.38 * W0, 0.38 * W0), 7.0):
        u = s / W0
        width = rnd.uniform(3.4, 4.5)
        lobes.append(Lobe(s, y, reach(y, rnd.uniform(10.0, 13.0), False), width, rnd.uniform(0.85, 1.0),
                          bed_z(u) + 2.6 - 2.0 * abs(u), rnd.uniform(7.0, 9.0), rnd.uniform(-1.4, 1.4),
                          rnd.uniform(-0.8, 0.8), core_heat(u) + 0.3 + rnd.uniform(-0.3, 0.3),
                          rnd.uniform(3.5, 4.8), hook=rnd.choice((-1, 1)) * rnd.uniform(0.8, 1.6),
                          droop=rnd.uniform(1.0, 2.0), front=0.3, wave=rnd.uniform(0.06, 0.12),
                          wave_phase=rnd.uniform(0, 2 * math.pi), flank=2.0 + 2.2 * abs(u)))
    return lobes


def head_lobes():
    """The head's front row: four broad billows rising from the layer at the column's front edge, overlapping (their
    rounded fronts make it, scalloped, cooler than their tops), their tongues sweeping back and up over the top;
    their widths are given as they are on the narrowing outline there."""
    rnd = random.Random(89)
    lobes = []
    for u in (-0.64, -0.21, 0.22, 0.65):
        u += rnd.uniform(-0.03, 0.03)
        edge = abs(u)
        y = Y_BOTTOM + 0.2 + 2.6 * edge ** 2 + rnd.uniform(0.0, 0.5)
        squeeze = OUTLINE.frame(y)[1] / W0
        width = rnd.uniform(5.0, 5.6) * (1 - 0.15 * edge) / squeeze
        lobes.append(Lobe(u * W0, y, rnd.uniform(13.0, 15.0), width, 0.6, -0.3,
                          rnd.uniform(7.0, 8.5) * (1 - 0.35 * edge),
                          math.copysign(1.2, u) * edge + rnd.uniform(-0.8, 0.8),
                          rnd.uniform(-0.8, 0.8), core_heat(u) - 0.6, rnd.uniform(4.0, 5.0),
                          hook=rnd.choice((-1, 1)) * 1.2, droop=1.2, front=0.34, wave=0.1,
                          wave_phase=rnd.uniform(0, 2 * math.pi), front_cool=2.6))
    return lobes


def tail_lobes():
    """The tail's end: tongues trailing off the column's back, the two biggest ending in the sprites' two tips (the
    tail's top row, columns 28-38 and 42-55 of the 72), two lower ones along its sides."""
    rnd = random.Random(13)
    lobes = []
    for u, y, length, width in ((-0.47, 21.0, 12.8, 5.0), (0.42, 20.0, 13.8, 5.4), (-0.85, 17.0, 11.5, 3.8),
                                (0.85, 16.0, 12.0, 4.0)):
        lobes.append(Lobe(u * W0, y, length, width, 0.85, bed_z(u) - 0.8, rnd.uniform(3.0, 4.0),
                          math.copysign(0.6, u), rnd.uniform(-0.5, 0.5), core_heat(u) - 0.5, 5.0,
                          hook=math.copysign(0.8, -u), droop=0.6, front=0.28, wave=0.08,
                          wave_phase=rnd.uniform(0, 2 * math.pi)))
    return lobes


def lobe_mesh(name, lobe, seg_top=7):
    """A flame lobe in the straight column: from its rounded front back along +y, its centre rising towards its tip
    and bending across, in an S, the tip curling over; round over its top (its underside flat), widest a quarter of
    the way back, tapering to a soft tip. Returns the object (in the straight column) and the heat of each vertex:
    hottest on the front and the top, the flanks cooler, the tongue cooling towards its tip, the base cooler."""
    L = lobe

    def spine(t):
        tip = smoothstep(0.62, 1.0, t)
        return Vector((L.s + L.curl * t ** 2.4 + L.wobble * math.sin(math.pi * t) + L.hook * tip * tip,
                       L.y + L.length * t,
                       L.base + L.lift * smoothstep(0.0, 1.0, t) ** 0.8 - L.droop * tip ** 2.5))

    def tangent(t):
        e = 1e-3
        return (spine(min(1.0, t + e)) - spine(max(0.0, t - e))).normalized()

    def half_width(t):
        t0 = L.front
        if t <= t0:
            return L.width * math.sqrt(max(0.0, 1 - (1 - t / t0) ** 2))
        ripple = 1 + L.wave * math.sin(2 * math.pi * 2.2 * t + L.wave_phase) * smoothstep(t0, t0 + 0.2, t)
        return L.width * ((1 - t) / (1 - t0)) ** 0.85 * ripple

    angles = [math.pi * i / seg_top for i in range(seg_top + 1)]  # over the top; the underside flat
    ts = [0.025, 0.08, 0.16, 0.26, 0.38, 0.5, 0.62, 0.73, 0.83, 0.91, 0.97]
    rings, values = [], []
    up_axis = Vector((0, 0, 1))
    for t in ts:
        c = spine(t)
        tan = tangent(t)
        across = tan.cross(up_axis)
        across = across.normalized() if across.length > 1e-6 else Vector((1, 0, 0))
        up = across.cross(tan).normalized()
        a = half_width(t)
        b = a * L.thick
        ring = []
        for th in angles:
            p = c + across * a * math.cos(th) + up * b * math.sin(th)
            p.z = max(p.z, -0.3)
            ring.append(p)
            facing = math.sin(th)
            h = L.heat + 0.5 - L.cool * smoothstep(0.25, 1.0, t) ** 1.2
            h -= L.front_cool * (1 - smoothstep(0.0, 0.35, t))
            h -= L.flank * (1 - facing) ** 1.5
            values.append(h - base_cooling(p.z))
        rings.append(ring)
    obj = k.loft(name, rings, None, start_point=spine(0.0), end_point=spine(1.0))
    values += [L.heat - 1.0, L.heat - L.cool - 1.0]
    return obj, values


def all_lobes():
    """Every lobe of the whole with the row it belongs to and whether it is bent on the middle's outline alone: the
    middle row's; the head's (the middle row's repeated a row lower, those under its front row left out, and its
    front row); the tail's (the middle row's repeated a row higher, cut short to end inside the outline, those too
    near its end left out, and its trailing tongues)."""
    out = []
    for lobe in periodic_lobes():
        out.append((lobe, "mid", True))
        below = lobe.moved(-PITCH)
        if below.y > Y_BOTTOM + 6.0 and (below.y > -21.0 or abs(below.s) < 0.45 * W0):
            out.append((below, "head", False))
        above = lobe.moved(PITCH)
        length = min(above.length, Y_TOP - 0.3 - above.y)
        if length >= 5.0:
            out.append((above.moved(0.0, length), "tail", False))
    out += [(lobe, "head", False) for lobe in head_lobes()]
    out += [(lobe, "tail", False) for lobe in tail_lobes()]
    return out


def build_lobes(bands):
    """The lobes' objects, each with the piece it belongs to (the piece whose 24 x 24 cell holds its front)."""
    owned = []
    for i, (lobe, row, periodic) in enumerate(all_lobes()):
        obj, values = lobe_mesh("lobe_%d" % i, lobe)
        for v in obj.data.vertices:
            v.co = bend(v.co, periodic)
        band_split(obj, values, bands)
        k.smooth(obj, 70)
        front = bend(Vector((lobe.s, lobe.y, 0.0)), periodic)
        col = "l" if front.x < -12.0 else "c" if front.x < 12.0 else "r"
        owned.append((obj, "fire_%s_%s" % (row, col)))
    return owned


# --- The whole and its pieces -------------------------------------------------------------------------------------

def join(name, objects):
    """Joins the objects into one (their custom normals kept)."""
    if len(objects) == 1:
        objects[0].name = name
        return objects[0]
    with bpy.context.temp_override(selected_editable_objects=objects, active_object=objects[0],
                                   selected_objects=objects):
        bpy.ops.object.join()
    objects[0].name = name
    objects[0].data.name = name
    return objects[0]


def copy_of(obj):
    new = obj.copy()
    new.data = obj.data.copy()
    bpy.context.scene.collection.objects.link(new)
    return new


def build():
    options = k.args()
    out = mk.outdir(options)
    only = options["only"].split(",") if "only" in options else None
    k.reset()
    bands = materials()
    bed = build_bed(bands)
    owned = build_lobes(bands)
    whole = [bed] + [obj for obj, _ in owned]
    bpy.context.view_layer.update()
    cap = next(mat for _, mat in bands if mat.name.endswith("@%d" % CAP))
    bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
    low, high = mk.bounds(whole)
    print("== whole: %d triangles, %d lobes, x %.2f..%.2f y %.2f..%.2f z %.2f..%.2f" % (
        mk.triangles(whole), len(owned), low.x, high.x, low.y, high.y, low.z, high.z))
    if "whole" in options:
        mk.export(whole, options["whole"])
    if "preview" in options:
        mk.preview(options["preview"] + "whole", whole, size=(72, 76), scale=8, distance=2.6)
    bpy.context.view_layer.update()
    sheet = os.path.join(options["check"], "enemy_K.png") if "check" in options else None
    for name, sprite, (cx, cy) in PIECES:
        if only and name not in only:
            continue
        parts = [cut(bed, (cx - 12.0, cx + 12.0, cy - 14.0, cy + 14.0), cap)]
        parts += [copy_of(obj) for obj, owner in owned if owner == name]
        parts = [p for p in parts if p is not None]
        mk.transform(parts, Matrix.Translation((-cx, -cy, 0.0)))
        piece = join(name, parts)
        bpy.context.view_layer.update()
        for src in whole:
            src.hide_render = True
        if sheet:
            mk.compare("%s (K %d)" % (name, sprite), mk.coverage([piece], 24, 28), k.sprite_mask(sheet, sprite))
        mk.report(name, [piece], os.path.join(out, name + ".glb"))
        if "preview" in options:
            mk.preview(options["preview"] + name, [piece])
        bpy.data.objects.remove(piece)
        for src in whole:
            src.hide_render = False


if __name__ == "__main__":
    build()
