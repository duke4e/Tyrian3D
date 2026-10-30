"""The Vulcan Cannon's needles (shots sheet sprites 67, 70, 245, 132, 133, 151, 152, 148, 107 and 108, all 1x1: 12 x 14
cells), modelled (2026-10-29, round 2 of the energy shots' models, after the Pulse-Cannon's pilot: until then they were
drawn as their sprites with volume and the automatic glow).

Who fires them (weapons as the item data numbers them; none is animated and none picks its sprite by direction):
  Vulcan Cannon front (port 7, the first shop, 600): 67 at power 1-6, 70 at 7-11, straight up the screen at 20 pixels a
    game frame and speeding up, a needle every one or two frames (every frame at power 11: twenty and more on screen),
    each a pixel or two to the side at random (del 98).
  Vulcan Cannon rear (port 15, 500): 132 (up and left) at power 1-2, 132 and 133 (up and right) at 3-8 (and a second
    132 at 8), the pairs 151 and 152 at 9-11; port 16 (the sidekicks' weapons) the same at its levels 8-11.
  Sidekicks: Single Shot Option and Satellite Marlo 67, Dual Shot Option 245, Vulcan Shot Option 148, Side Ship 107 and
    two 108s (and the special Dual Vulcan two 108s); the second player's charge cannon on rear port 15 (67, 70).
  Enemies, once Enemy Fire Override events give their turrets a frequency: weapons 98 and 100 (70: SAVARA, SAVARA Y),
    5 (245: ASTEROID2) and 221 (67: MINERS); they fly down the screen with the head up, as the sprites are drawn.

As the sprites draw them: 67 is a needle of fire 3 pixels wide and 11 rows long (columns 4-6), its middle column the
fire's ramp 7 from the head's yellow (0x7c at row 1, 0x7b, 0x7a) through orange (0x79, 0x78) and red (0x77, 0x75) to the
dark red of its tail (0x73-0x71, rows 8-10, one pixel wide), its side columns three to six shades cooler (0x76-0x72),
its tip a single 0x75 pixel (the very same pixels as the Pulse-Cannon's narrow bolts in 165). 70 is two of them two
pixels apart (columns 3-5 and 5-7, sharing column 5); 245 two of them seven pixels apart (columns 0-2 and 7-9). 132 is
the needle leaning 26 degrees left (its head at columns 0-2 of rows 0-3, its tail at column 5 of row 10), 133 its mirror
image; 151 two of 132's needles side by side four pixels apart (132's pixels a row lower and 132's four columns to the
right), 152 its mirror image. 148 is three needles one pixel wide, each ten rows long (0x75 at the tip, 0x7a, the yellow
0x7c, 0x79, 0x77, 0x75, then a flickering dark tail 0x73 0x71 0x73 0x71), side by side two columns apart (columns 3, 5
and 7), the middle one ahead, the right one two rows behind it and the left one four. 107 and 108 are the Side Ship's
embers: spindles 3 pixels wide and 8 rows long (rows 6-13), a dark red rim (0x70-0x72) round a hot middle (0x79, 0x7b at
row 9, 0x77), 108 one (columns 4-6), 107 two (columns 0-2 and 7-9).

The models (the pulse's way, leaner: these fly in dozens): every needle is a body of fire round on top and flat
underneath (the camera only ever sees shots from above), 2.5 pixels wide (a little slimmer than the sprite's 3, so that
it reads as a needle and not as the pulse's bolt), lofted along the screen's y from a rounded point (its first 1.8
pixels), full width to 0.45 of its length, then tapering straight to the tail's point where the sprite's tail ends. Its
fire is in four bands of ramp 7 (0x73 at the tail's tip, 0x76, 0x78, 0x7a round the head), each glowing in its own
colour (0.24-0.5), by a heat that falls along the needle as the sprite's middle column does and faster at its sides (so
that the colours lie in chevrons pointing back); the mesh's rings are the bands' borders (no face is cut). Down its
front half a hot spine stands out of the fire, a thin teardrop 5.8 pixels long, pale yellow at its front and yellow
behind (0x7d, 0x7c, glowing 0.6 and 0.56): the sprite's bright middle column, raised. Six materials, 156 triangles a
needle. The leaning needles are the same needle turned (yaw=, the main axis of 132's pixels: 26 degrees) and moved onto
the sprite's pixels (at=, fitted: --check --fit); the leaning pairs one model of two needles side by side 4 pixels
apart, turned the same ways (152 is 151's mirror image, and the two needles of a pair look alike, so turned the other
way it is 152; the sprite's pair is staggered 0.7 pixels along the needles, the model's level). 148's needles are
thinner (1.2 pixels wide, a longer tail), no spine, their heads yellow (0x7b; five bands, 0x73-0x7b). The Side Ship's
embers are spindles pointed at both ends, dark red (0x72, 0x74, 0x76 in rings round their hot middle) round a raised
lens of the hot colours (0x7b at its middle, 0x79 at its ends): five materials.
Each shot line's glow= (in place of the automatic glow, 13 pixels at 0.7 in the sprite's brightest colour, which would
swallow a needle) puts a small yellow halo (0x7b, 0.5-0.55) on the needles' heads, a little wider than they are.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera; the origin at the
sprite's centre (pixel 6, 7 of the cell: column c is x = c + 0.5 - 6, row r is y = 6.5 - r, its top edge y = 7 - r);
the needles stand on z = 0 (the game centres shot models in height on the player's layer).

models.cfg: the model lines and the shot lines are printed by the build (SHOTS below), e.g.
    model shot_vulcan        shots/shot_vulcan.glb
    shot shots 67  shot_vulcan        glow=8:0.55:123:-0.5:-3.5
    shot shots 132 shot_vulcan        yaw=334 at=-1.75:-0.5 glow=8:0.55:123:-3.6:-3.4

Run: Blender -b --factory-startup -P tools/blender/models/shots/polish_shot_vulcan.py -- [--only <name,...>]
     [--outdir <dir>] (default assets/models/shots) [--check <sheets dir>] (each model's top view against its sprites in
     <dir>/shots.png, from TYR3D_EXTRACT, turned and moved as their shot lines say; with --fit also the yaw and offset
     that fit each turned sprite best) [--preview <prefix>] (top, three-quarter and game-camera views)
"""
import math
import os
import sys

import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
ENEMIES = os.path.join(HERE, "..", "enemies")
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, ENEMIES)
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
import polish_machine_kit as mk  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402
from polish_flame_drop import monotone  # noqa: E402
from polish_launched_flames import lit, smoothstep, check_frames, turn  # noqa: E402
from polish_shot_pulse import mesh_from_rings, game_view  # noqa: E402

OUTDIR = os.path.join(HERE, "..", "..", "..", "..", "assets", "models", "shots")
TOP = 7.0  # the y of a 1x1 sprite's top edge

# --- The sprites (palette indices, '..' transparent): the three kinds as drawn ---------------------------------------

SPRITES = {
    67: """
.. .. .. .. .. 75 .. .. .. .. .. ..
.. .. .. .. 76 7c 75 .. .. .. .. ..
.. .. .. .. 77 7b 76 .. .. .. .. ..
.. .. .. .. 78 7a 78 .. .. .. .. ..
.. .. .. .. 76 79 76 .. .. .. .. ..
.. .. .. .. 75 78 74 .. .. .. .. ..
.. .. .. .. 74 77 74 .. .. .. .. ..
.. .. .. .. 73 75 73 .. .. .. .. ..
.. .. .. .. 72 73 72 .. .. .. .. ..
.. .. .. .. .. 72 .. .. .. .. .. ..
.. .. .. .. .. 71 .. .. .. .. .. ..
.. .. .. .. .. .. .. .. .. .. .. ..
.. .. .. .. .. .. .. .. .. .. .. ..
.. .. .. .. .. .. .. .. .. .. .. ..
""",
    148: """
.. .. .. .. .. 75 .. .. .. .. .. ..
.. .. .. .. .. 7a .. .. .. .. .. ..
.. .. .. .. .. 7c .. 75 .. .. .. ..
.. .. .. .. .. 79 .. 7a .. .. .. ..
.. .. .. 75 .. 77 .. 7c .. .. .. ..
.. .. .. 7a .. 75 .. 79 .. .. .. ..
.. .. .. 7c .. 73 .. 77 .. .. .. ..
.. .. .. 79 .. 71 .. 75 .. .. .. ..
.. .. .. 77 .. 73 .. 73 .. .. .. ..
.. .. .. 75 .. 71 .. 71 .. .. .. ..
.. .. .. 73 .. .. .. 73 .. .. .. ..
.. .. .. 71 .. .. .. 71 .. .. .. ..
.. .. .. 73 .. .. .. .. .. .. .. ..
.. .. .. 71 .. .. .. .. .. .. .. ..
""",
    108: """
.. .. .. .. .. .. .. .. .. .. .. ..
.. .. .. .. .. .. .. .. .. .. .. ..
.. .. .. .. .. .. .. .. .. .. .. ..
.. .. .. .. .. .. .. .. .. .. .. ..
.. .. .. .. .. .. .. .. .. .. .. ..
.. .. .. .. .. .. .. .. .. .. .. ..
.. .. .. .. .. 71 .. .. .. .. .. ..
.. .. .. .. 71 74 71 .. .. .. .. ..
.. .. .. .. 72 79 72 .. .. .. .. ..
.. .. .. .. 72 7b 72 .. .. .. .. ..
.. .. .. .. 72 79 72 .. .. .. .. ..
.. .. .. .. 71 77 71 .. .. .. .. ..
.. .. .. .. 70 74 70 .. .. .. .. ..
.. .. .. .. .. 72 .. .. .. .. .. ..
""",
}


# --- The kinds of needle ----------------------------------------------------------------------------------------------
# A kind: its outline along t (0 the head's tip, 1 the tail's): the head's cap (its length; its profile sin(u pi / 2)
# to the power cap_power, a rounded point; "point" for a spindle's two ends), the width where its body ends and where it
# starts tapering to the tail's point (fractions of the half-width) and the taper's power (under 1: fuller); the
# section's height over its half-width; the points round its upper half; where along it the fire is hottest (0: at the
# head); the heat along its middle line ((t, shade of ramp 7)) and how much cooler its sides are (ACROSS(t) times the
# square of the way out); its bands ((lowest heat, palette index, emission strength), the coolest first: the flat
# underside takes the coolest); the rings in the head (fractions of the way to the first border), between borders
# further apart than GAP and in the tail; and its core (a raised teardrop or lens of the hottest colours; None for
# none).

class Kind:
    def __init__(self, **values):
        self.__dict__.update(values)
        self.along_fn = monotone([p[0] for p in self.along], [p[1] for p in self.along])
        self.across_fn = monotone([p[0] for p in self.across], [p[1] for p in self.across])


# The Vulcan's needle (67): a 2.5-pixel needle, its head a rounded point (1.8 pixels), full width to 0.45 of its length,
# then tapering straight to the tail's point; four bands (0x73 the tail's tip to 0x7a round the spine).
NEEDLE = Kind(
    cap=0.16, cap_power=0.85, taper=(0.45, 1.0, 1.0), depth=0.92, segments=5, peak=0.0,
    along=((0.0, 11.8), (0.15, 11.8), (0.28, 10.6), (0.4, 9.2), (0.5, 8.0), (0.6, 6.8), (0.7, 5.3), (0.8, 3.8),
           (0.9, 2.5), (1.0, 1.3)),
    across=((0.0, 1.5), (0.15, 3.5), (0.35, 3.0), (0.6, 2.6), (0.85, 1.4), (1.0, 0.6)),
    bands=[(-99.0, 0x73, 0.24), (3.6, 0x76, 0.34), (6.0, 0x78, 0.42), (8.3, 0x7a, 0.5)],
    head_rings=(0.12, 0.45), gap=0.2, tail_rings=(0.5,),
    # The spine: where its tip is behind the head's tip (pixels), its length (pixels), its half-width (a fraction of
    # the needle's), how far it stands out of the fire's top, its points round, the rings along it, its bands along it
    # ((from t, palette index, emission)), its profile ("tear": round in front, tapering back).
    core=dict(behind=0.35, length=5.8, width=0.48, lift=0.18, segments=4, rings=(0.06, 0.2, 0.42, 0.66, 0.86),
              bands=((0.0, 0x7d, 0.6), (0.4, 0x7c, 0.56)), profile="tear"),
)

# The Vulcan Shot Option's thin needles (148): 1.2 pixels wide, a long tail, no spine: the head yellow.
THIN = Kind(
    cap=0.18, cap_power=0.85, taper=(0.4, 1.0, 1.0), depth=0.95, segments=4, peak=0.0,
    along=((0.0, 11.4), (0.2, 11.4), (0.32, 9.5), (0.45, 7.3), (0.56, 5.4), (0.68, 3.7), (0.85, 2.3), (1.0, 1.2)),
    across=((0.0, 1.0), (0.3, 1.4), (1.0, 0.6)),
    bands=[(-99.0, 0x73, 0.24), (3.4, 0x75, 0.31), (5.4, 0x77, 0.38), (7.4, 0x79, 0.46), (9.6, 0x7b, 0.54)],
    head_rings=(0.3,), gap=0.22, tail_rings=(0.5,),
    core=None,
)

# The Side Ship's ember (107, 108): a spindle 2.8 pixels wide, pointed at both ends, hottest a little ahead of its
# middle: dark red (its bands lying in rings round the hot middle) round a raised lens of the hot colours, wide and
# round like a coal's glow.
EMBER = Kind(
    cap="point", cap_power=1.0, taper=(0.5, 1.0, 0.0), depth=0.85, segments=6, peak=0.44,
    along=((0.0, 2.2), (0.12, 3.6), (0.3, 6.0), (0.44, 7.0), (0.58, 6.0), (0.76, 3.8), (0.9, 2.6), (1.0, 2.0)),
    across=((0.0, 0.6), (0.44, 1.6), (1.0, 0.6)),
    bands=[(-99.0, 0x72, 0.2), (3.2, 0x74, 0.26), (5.0, 0x76, 0.34)],
    head_rings=(0.4,), gap=0.2, tail_rings=(0.5,),
    core=dict(behind=1.3, length=5.2, width=0.62, lift=0.24, segments=6, rings=(0.08, 0.2, 0.34, 0.5, 0.66, 0.8, 0.92),
              bands=((0.0, 0x79, 0.46), (0.22, 0x7b, 0.56), (0.66, 0x79, 0.46)), profile="lens"),
)


# --- The needles of each model --------------------------------------------------------------------------------------
# A needle: its kind, its middle x, the y of its head's tip (the top edge of its first row) and of its tail's tip (the
# bottom edge of its last row), its half-width.

class Needle:
    def __init__(self, kind, x, first_row, last_row, half_width):
        self.kind, self.x, self.w = kind, x, half_width
        self.nose, self.tail = TOP - first_row, TOP - last_row - 1


def needle(x, first_row=0, last_row=10):
    return Needle(NEEDLE, x, first_row, last_row, 1.25)


def thin(x, first_row, last_row):
    return Needle(THIN, x, first_row, last_row, 0.6)


def ember(x):
    return Needle(EMBER, x, 6, 13, 1.4)


def column(c):
    """The x of a sprite column's middle."""
    return c + 0.5 - 6.0


# name: (the sprite it is authored as, its needles, what it is). The leaning pair is authored upright: two needles
# four pixels apart (151's needles, measured across them), level, on 67's line.
PAIR_GAP = 4.06
MODELS = [
    ("shot_vulcan", 67, [needle(column(5))], "one needle"),
    ("shot_vulcan_2", 70, [needle(column(4)), needle(column(6))], "two needles side by side, 2 pixels apart"),
    ("shot_vulcan_2w", 245, [needle(column(1)), needle(column(8))], "two needles 7 pixels apart"),
    ("shot_vulcan_2t", None, [needle(column(5) - PAIR_GAP / 2), needle(column(5) + PAIR_GAP / 2)],
     "two needles 4 pixels apart (the leaning pairs, upright)"),
    ("shot_vulcan_3", 148, [thin(column(5), 0, 9), thin(column(7), 2, 11), thin(column(3), 4, 13)],
     "three thin needles, staggered"),
    ("shot_vulcan_side", 108, [ember(column(5))], "an ember"),
    ("shot_vulcan_side_2", 107, [ember(column(1)), ember(column(8))], "two embers"),
]

# The shot lines: (sprite, model, yaw (degrees clockwise from up), at (dx, dy: screen pixels, dy down), glow (size,
# strength, palette index, dx, dy), comment). The leaning ones: the yaw of the sprite's needles (the main axis of their
# pixels), the offset that puts the turned model's footprint on the sprite's (--check --fit measures both).
GLOW = 0x7b
SHOTS = [
    (67, "shot_vulcan", 0, None, (8, 0.55, GLOW, -0.5, -3.5), "one needle (Vulcan Cannon front, power 1-6)"),
    (70, "shot_vulcan_2", 0, None, (10, 0.55, GLOW, -0.5, -3.5), "two needles (power 7-11)"),
    (245, "shot_vulcan_2w", 0, None, (12, 0.5, GLOW, -1.0, -3.5), "two needles apart (Dual Shot Option)"),
    (132, "shot_vulcan", 334, (-1.75, -0.5), (8, 0.55, GLOW, -3.6, -3.4), "leaning left (rear, power 1-8)"),
    (133, "shot_vulcan", 26, (2.65, -0.1), (8, 0.55, GLOW, 3.6, -3.4), "leaning right (rear, power 3-8)"),
    (151, "shot_vulcan_2t", 334, (0.5, 0.35), (10, 0.55, GLOW, -2.0, -3.2), "two leaning left (rear, power 9-11)"),
    (152, "shot_vulcan_2t", 26, (0.45, 0.85), (10, 0.55, GLOW, 2.0, -3.2), "two leaning right (rear, power 9-11)"),
    (148, "shot_vulcan_3", 0, None, (9, 0.5, GLOW, -0.5, -2.0), "three thin needles (Vulcan Shot Option)"),
    (108, "shot_vulcan_side", 0, None, (7, 0.5, GLOW, -0.5, 3.0), "an ember (Side Ship, Dual Vulcan)"),
    (107, "shot_vulcan_side_2", 0, None, (10, 0.5, GLOW, -1.0, 3.0), "two embers (Side Ship)"),
]


# --- Building ---------------------------------------------------------------------------------------------------------

def half_width(n, t):
    """The needle's half-width at t (0 the head's tip, 1 the tail's)."""
    kind = n.kind
    start, width, power = kind.taper
    t = min(max(t, 0.0), 1.0)
    if kind.cap == "point":  # a spindle: rounded points at both ends (a superellipse along it)
        u = abs(2.0 * t - 1.0)
        return n.w * max(0.0, 1.0 - u ** 2.6) ** 0.55
    if t < kind.cap:
        return n.w * math.sin(0.5 * math.pi * t / kind.cap) ** kind.cap_power
    if t < start:
        return n.w * (1.0 + (width - 1.0) * smoothstep(kind.cap, start, t))
    return n.w * width * ((1.0 - t) / (1.0 - start)) ** power


def top_height(n, x, y):
    """The height of the needle's fire over z = 0 at (x, y) (0 outside it)."""
    t = (n.nose - y) / (n.nose - n.tail)
    if not 0.0 <= t <= 1.0:
        return 0.0
    w = half_width(n, t)
    u = (x - n.x) / w if w > 1e-6 else 2.0
    return w * n.kind.depth * math.sqrt(1.0 - u * u) if abs(u) < 1.0 else 0.0


def heat(n, angle, t):
    """The fire's heat at the angle round the top (0 the right side, pi / 2 the top, pi the left side) and t."""
    u = min(abs(math.cos(angle)), 1.0)
    return n.kind.along_fn(t) - n.kind.across_fn(t) * u * u


def crossing(n, angle, value, sign, steps=300):
    """Where (t), going from the hottest point towards the tail (sign +1) or the head (-1), the heat at the angle first
    falls below value (the hottest point if it is below it there; the end if it never does)."""
    peak = n.kind.peak
    end = 1.0 if sign > 0 else 0.0
    if heat(n, angle, peak) < value:
        return peak
    previous = peak
    for i in range(1, steps + 1):
        t = peak + (end - peak) * i / steps
        if heat(n, angle, t) < value:
            lo, hi = previous, t
            for _ in range(30):
                mid = (lo + hi) / 2
                if heat(n, angle, mid) < value:
                    hi = mid
                else:
                    lo = mid
            return (lo + hi) / 2
        previous = t
    return end


def side_borders(n, angles, sign):
    """The bands' borders on one side of the hottest point (hottest first), each a t per angle, each further from it
    than the one before at every angle."""
    peak = n.kind.peak
    bands = n.kind.bands
    lines = []
    for lowest, _, _ in reversed(bands[1:]):
        line = [crossing(n, a, lowest, sign) for a in angles]
        lines.append(line)
    gap = 0.012
    for b, line in enumerate(lines):
        for j in range(len(angles)):
            before = lines[b - 1][j] if b > 0 else peak
            if sign > 0:
                line[j] = min(max(line[j], before + gap), 0.985 - gap * (len(lines) - 1 - b))
            else:
                line[j] = max(min(line[j], before - gap), 0.015 + gap * (len(lines) - 1 - b))
    return lines


def fill(curves, line, following, band, gap):
    """Rings between two borders further apart than gap (t) somewhere."""
    if following is None:
        return
    extra = int(max(abs(b - a) for a, b in zip(line, following)) / gap)
    for j in range(1, extra + 1):
        f = j / (extra + 1)
        curves.append(([a + (b - a) * f for a, b in zip(line, following)], band))


def ring_curves(n, angles):
    """The rings of the needle's mesh as curves t(angle), from the head's tip to the tail's: its bands' borders, rings
    between them where they lie far apart, in the head and in the tail. Returns [(t per angle, band of the faces after
    it)] and the bands of the head's and the tail's fans."""
    kind = n.kind
    hottest = len(kind.bands) - 1
    back = side_borders(n, angles, +1)
    curves = []
    if kind.peak > 0.0:
        front = side_borders(n, angles, -1)  # (hottest first: nearest the peak)
        coolest = front[-1]
        for f in kind.head_rings:
            curves.append(([f * t for t in coolest], 0))
        for i, line in enumerate(reversed(front)):  # from the coolest border towards the peak
            band = i + 1
            curves.append((line, band))
            following = list(reversed(front))[i + 1] if i + 1 < len(front) else [kind.peak] * len(angles)
            fill(curves, line, following, band, kind.gap)
        curves.append(([kind.peak] * len(angles), hottest))
        head_band = 0
    else:
        for f in kind.head_rings:
            curves.append(([f * t for t in back[0]], hottest))
        head_band = hottest
    for i, line in enumerate(back):
        band = hottest - 1 - i
        curves.append((line, band))
        fill(curves, line, back[i + 1] if i + 1 < len(back) else None, band, kind.gap)
    for f in kind.tail_rings:
        curves.append(([a + (1.0 - a) * f for a in back[-1]], 0))
    return curves, head_band, 0


def sheath(name, n, materials):
    """The needle's fire: rings along it on the bands' borders, each point at its own t round the section."""
    count = n.kind.segments
    angles = [math.pi * j / count for j in range(count + 1)]
    length = n.nose - n.tail
    curves, head_band, tail_band = ring_curves(n, angles)
    rings = []
    for ts, _ in curves:
        ring = []
        for a, t in zip(angles, ts):
            w = max(half_width(n, t), 0.02)
            ring.append(Vector((n.x + w * math.cos(a), n.nose - t * length, w * n.kind.depth * math.sin(a))))
        rings.append(ring)
    bands = [curves[i][1] for i in range(len(curves) - 1)] + [head_band, tail_band]
    obj = mesh_from_rings(name, rings, bands, ((n.x, n.nose, 0.0), (n.x, n.tail, 0.0)), materials, 0)
    return k.smooth(obj, 70)


def core(name, n, materials):
    """The spine (a teardrop along the needle, round at its front, pointing back) or the ember's lens (pointed at both
    ends), standing out of the fire's top on its middle line; its bands along it."""
    c = n.kind.core
    front = n.nose - c["behind"]
    length = c["length"]
    w0 = c["width"] * n.w
    bands = c["bands"]
    ts = sorted(set(c["rings"]) | {b[0] for b in bands[1:]})
    angles = [math.pi * j / c["segments"] for j in range(c["segments"] + 1)]
    rings = []
    for t in ts:
        y = front - t * length
        if c["profile"] == "tear":
            f = math.sqrt(max(0.0, 1.0 - (1.0 - t / 0.3) ** 2)) if t < 0.3 else ((1.0 - t) / 0.7) ** 0.9
        else:
            f = math.sin(math.pi * t) ** 0.5
        w = max(w0 * f, 0.02)
        h = top_height(n, n.x, y) + c["lift"] * f
        rings.append([Vector((n.x + w * math.cos(a), y, h * math.sin(a))) for a in angles])

    def band_at(t):
        return max(i for i, b in enumerate(bands) if t >= b[0] - 1e-9)
    faces = [band_at(t) for t in ts[:-1]] + [0, len(bands) - 1]
    obj = mesh_from_rings(name, rings, faces, ((n.x, front, 0.0), (n.x, front - length, 0.0)), materials, 0)
    return k.smooth(obj, 80)


def build_model(name, needles):
    materials = {}

    def mats(bands):
        out = []
        for _, index, glow in bands:
            key = (index, glow)
            if key not in materials:
                materials[key] = lit(f"vulcan_{index:02x}", index, glow, roughness=0.5 if glow < 0.5 else 0.4)
            out.append(materials[key])
        return out
    parts = []
    for i, n in enumerate(needles):
        parts.append(sheath(f"{name}_needle{i}", n, mats(n.kind.bands)))
        if n.kind.core is not None:
            parts.append(core(f"{name}_core{i}", n, mats(n.kind.core["bands"])))
    return triangulate(parts)


# --- Checks -----------------------------------------------------------------------------------------------------------

def placement(yaw, at):
    """The shot line's turn and offset as one matrix (model coordinates: at's dy is down the screen)."""
    dx, dy = at if at is not None else (0.0, 0.0)
    return Matrix.Translation((dx, -dy, 0.0)) @ turn(yaw)


def fit(sheets, sprite, yaw):
    """The offset (at, 0.05 pixels) that puts the model turned by yaw best on the sprite (outline and colours,
    shot_kit's raster of the top view, from where the footprints' middles meet), and the main axis of the sprite's
    pixels (the yaw that would turn an upright needle onto them): returns ((dx, dy), score, overlap, axis, where the
    middles meet)."""
    import numpy as np
    import shot_kit as sk
    tris, colours = sk.top_triangles()
    target = sk.sprite_image(sheets, "shots", sprite)
    t = math.radians(yaw)
    c, s = math.cos(t), math.sin(t)
    turned = tris.copy()
    turned[..., 0] = tris[..., 0] * c + tris[..., 1] * s
    turned[..., 1] = -tris[..., 0] * s + tris[..., 1] * c
    xs = np.arange(12) + 0.5 - 6.0
    ys = 6.5 - np.arange(14)
    gx, gy = np.meshgrid(xs, ys)

    def middle(weights):
        return (gx * weights).sum() / weights.sum(), (gy * weights).sum() / weights.sum()
    mask = target[0].astype(float)
    sx, sy = middle(mask)
    cov = sk.raster((turned, colours), 0)[0]
    mx, my = middle(cov)

    def score(dx, dy):
        moved = turned.copy()
        moved[..., 0] += dx
        moved[..., 1] -= dy
        cov, rgb = sk.raster((moved, colours), 0)
        return sk.overlap(cov, target[0]) - 0.6 * sk.colour_distance(cov, rgb, target), sk.overlap(cov, target[0])
    best = None
    dx0, dy0 = sx - mx, -(sy - my)
    for dx in np.arange(dx0 - 0.6, dx0 + 0.61, 0.1):
        for dy in np.arange(dy0 - 0.6, dy0 + 0.61, 0.1):
            sc, ov = score(dx, dy)
            if best is None or sc > best[0]:
                best = (sc, ov, dx, dy)
    # The sprite's main axis (clockwise from up).
    px, py = gx[target[0]] - sx, gy[target[0]] - sy
    cxx, cyy, cxy = (px * px).mean(), (py * py).mean(), (px * py).mean()
    axis = 0.5 * math.degrees(math.atan2(2 * cxy, cyy - cxx))
    sc, ov, dx, dy = best
    return (round(dx * 20) / 20, round(dy * 20) / 20), sc, ov, axis, (dx0, dy0)


def cfg_lines(only=None):
    """The models.cfg lines: the model lines, then the shot lines, their options in aligned columns (at=, yaw=, glow=)
    and each with its comment."""
    names = [m[0] for m in MODELS if only is None or m[0] in only]
    width = max(len(n) for n in names)
    lines = [f"model {n.ljust(width)} shots/{n}.glb" for n in names]
    rows = []
    for sprite, name, yaw, at, glow, comment in SHOTS:
        if only is not None and name not in only:
            continue
        size, strength, colour, gx, gy = glow
        rows.append([f"shot shots {str(sprite).ljust(3)} {name.ljust(width)}",
                     f"at={at[0]:g}:{at[1]:g}" if at is not None else "", f"yaw={yaw:g}" if yaw else "",
                     f"glow={size:g}:{strength:g}:{colour}:{gx:g}:{gy:g}", comment])
    widths = [max(len(r[i]) for r in rows) for i in range(4)]
    out = []
    for r in rows:
        cells = [r[0]] + [r[i].ljust(widths[i]) for i in range(1, 4) if widths[i]]
        out.append(" ".join(cells) + " # " + r[4])
    return lines + out


# --- Build ------------------------------------------------------------------------------------------------------------

def build():
    options = k.args()
    only = set(options["only"].split(",")) if "only" in options else None
    outdir = options.get("outdir", OUTDIR)
    for name, sprite, needles, what in MODELS:
        if only is not None and name not in only:
            continue
        k.reset()
        parts = build_model(name, needles)
        bpy.context.view_layer.update()
        print(f"== {name} (shots {sprite}): {what}")
        if "check" in options:
            sheet = os.path.join(options["check"], "shots.png")
            for shot, model, yaw, at, _, comment in SHOTS:
                if model != name:
                    continue
                check_frames(parts, sheet, [(shot, placement(yaw, at), f"shots {shot} ({comment})")],
                             move_to_frame=False)
                if "fit" in options and (yaw or at is not None):
                    (dx, dy), sc, ov, axis, (cx, cy) = fit(options["check"], shot, yaw)
                    print(f"   fit shots {shot} at yaw {yaw}: at={dx:g}:{dy:g} (score {sc:.3f}, overlap {ov:.3f}; the "
                          f"middles meet at {cx:.2f}:{cy:.2f}); the sprite's main axis {axis:.1f} degrees")
        bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
        mk.report(name, parts, os.path.join(outdir, name + ".glb"))
        if "preview" in options:
            game_view(options["preview"] + name, parts)
    print("models.cfg:")
    for line in cfg_lines(only):
        print("  " + line)


if __name__ == "__main__":
    build()
