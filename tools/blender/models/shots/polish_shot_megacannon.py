"""The Mega Cannon's shots (shots sheet sprites 65 and 64; shots2 sprites 98, 99, 117 and 118, and 96, 97, 115 and 116:
all 1x1, 12 x 14 cells), modelled (2026-10-29, the second round of the energy shots' models; until then each was drawn
as its sprite with volume and the automatic glow). Built with polish_shot_fireball.py's kit (the pulse's method:
half-bodies on the bands' borders, a raised core); the Mega Cannon's power 5 shot is the fireballs' flare (75).

Who fires them: the Mega Cannon (front port 3, shop 1:9, 1000), straight up the screen, slowly (2-3 pixels a game frame,
accelerating), a volley every 8 frames:
  power  1: 65               power  5: 75 75 (the flare)                  power  9: blast (yellow)
  power  2: 65 65            power  6: blast (blue)                        power 10: blast (yellow) + 65 65
  power  3: 64               power  7: blast (blue) + 65 65 (14 out)       power 11: two blasts (yellow) side by side
  power  4: 65 65 65         power  8: two blasts (blue) side by side (12 out)
A blast is four sprites the game moves together (shots2 98 99 above 117 118, 6 out and 7 up or down; yellow: 96 97
above 115 116), each a shot of its own that flies on through what it hits (damage 250 and over). Enemies: weapon 92
(65: SAVARA, SOH JIN, SAVARA V, ** ALE **, SAVARA Y, SAVARA IV, SURFACE, DESERTRUN, TIME WAR, SQUADRON, by fire
override) and 60 (64: ASTEROID?), falling down the screen as drawn.

As the sprites draw them:
- 65 a drop of blue plasma (ramp 9) 8 pixels wide (columns 2-9) and 10 long: a round top (rows 0-1), its hottest
  pixels (0x9c) in its upper middle (row 3), darker blue round them and a near-black rim, its lower part breaking into
  three drips (columns 2 and 9 down to row 8, the middle columns down to row 9) with dark gaps between them (columns 3
  and 8). 64 the same in the fire's ramp 7 (0x7d at its hottest).
- the blasts: together 24 x 28 (the shared corner the blast's middle): an egg of white-hot plasma 22 wide, the white
  (shots2: 0x8f, ramp 8's white-blue; yellow: 0x7f) filling most of it inside a rim 3-5 pixels wide of light blue
  (0x8b-0x8e), blue (0x99-0x9c) and dark blue (0x92-0x97) (yellow: 0x7c-0x7e, 0x77-0x7b, 0x72), its lower half breaking
  into streaks of white and blue (yellow and orange) that reach down to the rim: a ball of plasma trailing flames.

The models:
- the drops (shot_megacannon: 65; _2: 64): polish_shot_fireball.build_drop: a body of plasma round on top and flat
  underneath, lofted along the screen's y, its heat rising from the dark rim of its top to its hot upper middle, then
  falling down to its middle drip; the side drips small lofts of their own (their roots inside the body); a small raised
  core on the hot spot (0x9c and 0x9b; 64: 0x7d and 0x7b).
- the blasts: one dome (polish_shot_fireball.Dome) over the egg (the outline of the four sprites' pixels, smoothed),
  rings round a hot spot a pixel above its middle, the heat a plateau out to well past the middle (pale cyan 0x8c;
  yellow 0x7d), then falling through the rim's bands (light blue, blue, dark blue; yellow, orange, red); the bands'
  borders wave as flame tongues reaching down its lower half; a raised oval of white (0x8f, 0x8e; 0x7f, 0x7e) on its
  upper middle (dome_core, following the dome's top). Built whole and cut into the four sprites' pieces
  (polish_machine_kit.cut: each piece keeps the whole's shading across the cuts, the cuts closed in the core's white),
  each moved so that its sprite's centre is its origin: drawn at their own places they meet again. The pieces' model
  lines take "origin" (drawn at their own origin, not centred in height each on its own bounds), their shot lines
  height= half the blast's height down (centred on the player's layer as the other shots are).

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera; a drop's origin at
its sprite's centre (pixel 6, 7 of the cell: column c is x = c + 0.5 - 6, row r is y = 6.5 - r); the blast built round
the four sprites' shared corner (whole column c, row r: x = c + 0.5 - 12, y = 13.5 - r), each piece moved onto its own
sprite's centre; built on z = 0.

models.cfg: see the block's comment.

Run: Blender -b --factory-startup -P tools/blender/models/shots/polish_shot_megacannon.py -- [--only <name,...>]
     [--outdir <dir>] (default assets/models/shots) [--check <sheets dir>] (the drops' and each piece's silhouette,
     and the whole blast's against its four sprites) [--preview <prefix>]
"""
import math
import os
import sys

import bpy
from mathutils import Matrix

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polish_shot_fireball as kit  # noqa: E402
from polish_shot_fireball import k, mk, triangulate, view  # noqa: E402
from polish_launched_flames import grid  # noqa: E402

# --- The drops --------------------------------------------------------------------------------------------------------

# 65 as drawn: the top's tip at row 0's top edge (y 7), the middle drip's at row 9's bottom edge (y -3); half-width
# (t: 0 the top, 1 the middle drip's tip).
DROP = dict(
    nose=7.0, tail=-3.0, depth=0.88, segments=12,
    width=((0.0, 0.0), (0.012, 1.0), (0.05, 2.15), (0.15, 3.15), (0.25, 3.85), (0.35, 4.0), (0.52, 4.0), (0.6, 3.75),
           (0.67, 3.1), (0.75, 2.5), (0.85, 1.8), (0.93, 1.05), (1.0, 0.0)),
    # the heat: hottest a row and a half under the top's tip, falling to the rim (half-axes 4 across, 3.6 up, 5 down)
    # and down the middle drip
    heat=kit.blob_heat((0.0, 3.4), 4.0, 3.6, 5.0,
                       ((0.0, 12.0), (0.15, 11.0), (0.3, 9.5), (0.5, 8.0), (0.7, 6.0), (0.85, 4.0), (1.0, 2.0),
                        (1.2, 0.5), (2.0, 0.2)),
                       ((-3.0, 0.2), (-2.5, 0.4), (-1.5, 1.2), (0.0, 99.0))),
    # the side drips: x, root y (inside the body), tip y (row 8's bottom edge), half-width; heat along them
    tongues=[(-3.4, 1.8, -1.6, 0.58), (3.4, 1.8, -1.6, 0.58)],
    tongue_along=((0.0, 4.5), (0.4, 3.4), (0.7, 2.2), (1.0, 1.0)),
    tongue_across=((0.0, 1.0), (1.0, 1.0)),
    core=(0.0, 3.45, 1.45, 1.3, 0.3),
    waves=(2.5, 0.02, 1.9),
)
# The bands: blue (ramp 9) for 65, the fire (ramp 7) for 64; the cores.
DROP_BANDS = {
    "blue": [(-99.0, 0x91, 0.2), (2.2, 0x93, 0.24), (4.2, 0x95, 0.3), (6.0, 0x97, 0.36), (7.8, 0x99, 0.42),
             (9.4, 0x9a, 0.48)],
    "fire": [(-99.0, 0x71, 0.2), (2.2, 0x73, 0.24), (4.2, 0x75, 0.31), (6.0, 0x77, 0.38), (7.8, 0x79, 0.46),
             (9.4, 0x7a, 0.5)],
}
DROP_CORE_BANDS = {
    "blue": ((0.0, 0x9c, 0.56), (0.55, 0x9b, 0.52)),
    "fire": ((0.0, 0x7d, 0.58), (0.55, 0x7b, 0.52)),
}

# --- The blasts -------------------------------------------------------------------------------------------------------

BLAST_SPRITES = {
    98: """
.. .. .. .. .. .. .. 92 92 95 97 97
.. .. .. .. .. .. 92 95 97 9a 9b 9c
.. .. .. .. .. 92 97 99 9b 9d 89 8b
.. .. .. .. .. 95 99 9b 9e 8b 8e 8e
.. .. .. .. 92 97 9c 8b 8e 8e 8f 8f
.. .. .. 92 97 9c 8b 8e 8f 8f 8f 8f
.. .. .. 97 9c 8b 8e 8f 8f 8f 8f 8f
.. .. 92 9a 9c 8d 8f 8f 8f 8f 8f 8f
.. .. 97 9c 8b 8e 8f 8f 8f 8f 8f 8f
.. .. 97 9c 8b 8e 8f 8f 8f 8f 8f 8f
.. 92 9a 9c 8d 8f 8f 8f 8f 8f 8f 8f
.. 97 9c 8b 8e 8f 8f 8f 8f 8f 8f 8f
.. 97 9c 8d 8f 8f 8f 8f 8f 8f 8f 8f
.. 97 9b 8d 8f 8f 8f 8f 8f 8f 8f 8f
""",
    99: """
97 97 95 92 .. .. .. .. .. .. .. ..
9c 9b 9a 97 95 92 .. .. .. .. .. ..
8b 89 9d 9b 99 97 92 .. .. .. .. ..
8e 8e 8b 9e 9b 99 95 .. .. .. .. ..
8f 8f 8e 8e 8b 9c 97 92 .. .. .. ..
8f 8f 8f 8f 8e 8b 9c 97 92 .. .. ..
8f 8f 8f 8f 8f 8e 8b 9c 97 .. .. ..
8f 8f 8f 8f 8f 8f 8d 9c 9a 92 .. ..
8f 8f 8f 8f 8f 8f 8e 8b 9c 97 .. ..
8f 8f 8f 8f 8f 8f 8e 8d 9c 97 .. ..
8f 8f 8f 8f 8f 8f 8f 8d 9c 9a 92 ..
8f 8f 8f 8f 8f 8f 8f 8e 8b 9c 97 ..
8f 8f 8f 8f 8f 8f 8e 8f 8d 9c 97 ..
8f 8f 8f 8f 8f 8f 9f 8f 9f 9c 97 ..
""",
    117: """
.. 97 9a 89 8f 9f 8f 8f 8f 8f 8f 8f
.. 97 99 9c 8c 9d 8e 8f 8f 8f 8f 8f
.. 92 97 9c 8a 9b 8f 8f 8f 8f 8d 8f
.. .. 97 99 86 9a 8f 8f 8f 8f 8e 8f
.. .. 92 97 9b 96 9c 8f 8f 8e 8d 8f
.. .. .. 97 99 97 9b 8b 9e 8e 9e 8f
.. .. .. 92 97 98 9a 8a 9c 8a 9c 8f
.. .. .. .. 92 94 98 8f 9b 8b 9c 8e
.. .. .. .. .. 92 98 88 9a 87 9c 8b
.. .. .. .. .. .. 97 9c 99 9c 99 89
.. .. .. .. .. .. 92 97 99 9a 99 9c
.. .. .. .. .. .. .. 92 95 99 97 99
.. .. .. .. .. .. .. .. 92 96 92 97
.. .. .. .. .. .. .. .. .. 92 .. 92
""",
    118: """
8f 8f 8f 8f 8f 8f 9c 8f 9c 9b 97 ..
8f 8f 8f 8f 8f 8f 9b 8a 99 9a 97 ..
8f 8d 8f 8f 8f 8f 9b 9e 99 97 92 ..
8f 8e 8f 8f 8f 8f 9a 9c 99 97 .. ..
8d 9e 8f 8f 8f 8f 9a 9a 97 92 .. ..
9c 9c 8f 9f 8f 8f 99 99 97 .. .. ..
9b 9c 8f 9b 8f 9f 99 94 92 .. .. ..
9b 9b 8e 9e 8d 9c 94 92 .. .. .. ..
8d 9a 9c 99 8d 9b 94 .. .. .. .. ..
9c 99 8b 98 9c 97 92 .. .. .. .. ..
9a 98 9b 98 97 92 .. .. .. .. .. ..
99 97 9a 95 92 .. .. .. .. .. .. ..
97 92 96 92 .. .. .. .. .. .. .. ..
92 .. 92 .. .. .. .. .. .. .. .. ..
""",
    96: """
.. .. .. .. .. .. .. .. 72 75 77 77
.. .. .. .. .. .. 72 75 77 7a 7c 7c
.. .. .. .. .. 72 77 79 7b 7c 7d 7d
.. .. .. .. .. 75 79 7b 7c 7d 7e 7e
.. .. .. .. 72 77 7c 7d 7e 7e 7f 7f
.. .. .. 72 77 7c 7d 7e 7f 7f 7f 7f
.. .. .. 77 7c 7d 7e 7f 7f 7f 7f 7f
.. .. 72 7a 7c 7d 7f 7f 7f 7f 7f 7f
.. .. 77 7c 7d 7e 7f 7f 7f 7f 7f 7f
.. .. 77 7c 7d 7e 7f 7f 7f 7f 7f 7f
.. 72 7a 7c 7d 7f 7f 7f 7f 7f 7f 7f
.. 77 7c 7d 7e 7f 7f 7f 7f 7f 7f 7f
.. 77 7c 7d 7f 7e 7f 7f 7f 7f 7f 7f
.. 77 7c 7b 7f 7e 7f 7f 7f 7f 7f 7f
""",
    97: """
77 77 75 72 72 .. .. .. .. .. .. ..
7c 7c 7a 77 75 72 .. .. .. .. .. ..
7d 7d 7c 7b 79 77 72 .. .. .. .. ..
7e 7e 7d 7c 7b 79 75 .. .. .. .. ..
7f 7f 7e 7e 7d 7c 77 72 .. .. .. ..
7f 7f 7f 7f 7e 7d 7c 77 72 .. .. ..
7f 7f 7f 7f 7f 7e 7d 7c 77 .. .. ..
7f 7f 7f 7f 7f 7f 7d 7c 7a 72 .. ..
7f 7f 7f 7f 7f 7f 7e 7d 7c 77 .. ..
7f 7f 7f 7f 7f 7f 7e 7d 7c 77 .. ..
7f 7f 7f 7f 7f 7f 7f 7d 7c 7a 72 ..
7f 7f 7f 7f 7f 7f 7f 7e 7d 7c 77 ..
7f 7f 7f 7f 7f 7f 7f 7f 7d 7c 77 ..
7f 7f 7f 7f 7f 7f 7f 7f 7d 7b 77 ..
""",
    115: """
.. 77 7b 7a 7f 7c 7f 7f 7f 7f 7f 7f
.. 77 7a 79 7f 7b 7f 7f 7f 7f 7f 7f
.. 72 77 79 7c 7b 7f 7f 7f 7f 7d 7f
.. .. 77 79 7c 7a 7f 7f 7f 7f 7e 7f
.. .. 72 77 7a 7a 7f 7f 7f 7f 7d 7d
.. .. .. 77 79 79 7f 7f 7e 7f 7c 7c
.. .. .. 72 74 79 7d 7f 7b 7f 7c 7b
.. .. .. .. 72 74 7c 7d 7d 7e 7b 7b
.. .. .. .. .. 74 7c 7d 79 7c 7a 7d
.. .. .. .. .. 72 77 7c 78 7d 79 7c
.. .. .. .. .. .. 72 77 78 7b 78 7a
.. .. .. .. .. .. .. 72 75 7a 77 79
.. .. .. .. .. .. .. .. 72 76 72 77
.. .. .. .. .. .. .. .. .. 72 .. 72
""",
    116: """
7f 7f 7f 7f 7f 7f 7d 7f 7d 7a 77 ..
7f 7f 7f 7f 7f 7f 7d 7f 7c 79 77 ..
7f 7d 7f 7f 7f 7f 7b 7d 7c 77 72 ..
7f 7e 7f 7f 7f 7f 7a 7d 79 77 .. ..
7f 7d 7e 7f 7f 7c 76 7b 77 72 .. ..
7f 7d 7e 7e 7f 7b 77 79 77 .. .. ..
7f 7c 7d 7c 7f 7a 78 77 72 .. .. ..
7e 7c 7d 7b 7d 78 74 72 .. .. .. ..
7d 7c 7e 7a 7d 78 72 .. .. .. .. ..
7e 79 7b 79 7c 77 .. .. .. .. .. ..
7c 79 7a 79 77 72 .. .. .. .. .. ..
79 77 79 75 72 .. .. .. .. .. .. ..
77 72 76 72 .. .. .. .. .. .. .. ..
72 .. 72 .. .. .. .. .. .. .. .. ..
""",
}
# The pieces: (shots2 sprite, its box in the whole (x0, x1, y0, y1)); blue 98 99 / 117 118, yellow 96 97 / 115 116.
PIECES = {
    "blue": [(98, (-12.0, 0.0, 0.0, 14.0)), (99, (0.0, 12.0, 0.0, 14.0)), (117, (-12.0, 0.0, -14.0, 0.0)),
             (118, (0.0, 12.0, -14.0, 0.0))],
    "yellow": [(96, (-12.0, 0.0, 0.0, 14.0)), (97, (0.0, 12.0, 0.0, 14.0)), (115, (-12.0, 0.0, -14.0, 0.0)),
               (116, (0.0, 12.0, -14.0, 0.0))],
}
# The blast: its height over z = 0 at its middle (a dome over the egg), the hot spot (the rings' centre); the heat:
# white (WHITE) out to 1 - RIM(phi) of the way to the outline (RIM: degrees counter-clockwise from right: the rim's
# share of the way), then falling to RIM_HEAT at the outline (to the power FALL); the flame tongues' waves along the
# borders (how many round the blast, how far (u) at its bottom, where they start fading (degrees from straight down)
# and a little everywhere); the bands; the core (its middle x, y, its half-axes, lift: an oval on the dome's top).
BLAST_HEIGHT = 5.4
BLAST_HOT = (0.0, 1.0)
WHITE, RIM_HEAT, FALL = 16.0, 2.0, 1.25
RIM = ((0, 0.3), (45, 0.34), (90, 0.4), (135, 0.34), (180, 0.3), (225, 0.36), (270, 0.46), (315, 0.36))
TONGUES = (13, 0.17, 80.0, 0.0)
BLAST_BANDS = {
    "blue": [(-99.0, 0x92, 0.22), (4.5, 0x96, 0.3), (7.5, 0x99, 0.4), (10.0, 0x9c, 0.48), (12.5, 0x8a, 0.5),
             (14.2, 0x8c, 0.54)],
    "yellow": [(-99.0, 0x72, 0.22), (4.5, 0x76, 0.33), (7.5, 0x79, 0.46), (10.0, 0x7b, 0.52), (12.5, 0x7c, 0.56),
               (14.2, 0x7d, 0.58)],
}
BLAST_CORE_BANDS = {
    "blue": ((0.0, 0x8f, 0.6), (0.55, 0x8e, 0.58)),
    "yellow": ((0.0, 0x7f, 0.62), (0.55, 0x7e, 0.6)),
}
BLAST_CORE = (0.0, 1.8, 6.4, 8.4, 0.55)  # (its middle x, y, half-axes, lift)

def blast_outline(colour):
    """The blast's outline (its four sprites' pixels, row by row), smoothed: a closed polygon round the whole's
    middle."""
    rows = []
    tl, tr, bl, br = [BLAST_SPRITES[s].strip("\n").splitlines() for s, _ in PIECES[colour]]
    for left, right in list(zip(tl, tr)) + list(zip(bl, br)):
        cells = left.split() + right.split()
        cols = [c for c, t in enumerate(cells) if t != ".."]
        rows.append((cols[0], cols[-1]))
    right_side, left_side = [], []
    for r, (c0, c1) in enumerate(rows):
        y = 13.5 - r
        right_side.append((c1 + 1 - 12.0, y))
        left_side.append((c0 - 12.0, y))
    points = [((rows[0][0] + rows[0][1] + 1) / 2 - 12.0, 14.0)] + right_side + \
        [((rows[-1][0] + rows[-1][1] + 1) / 2 - 12.0, -14.0)] + list(reversed(left_side))
    return mk.chaikin(points, iterations=3)


def ray_to_polygon(points, origin, phi):
    """How far from origin along the angle phi the polygon's boundary lies."""
    ox, oy = origin
    dx, dy = math.cos(phi), math.sin(phi)
    best = None
    for (ax, ay), (bx, by) in zip(points, points[1:] + points[:1]):
        ex, ey = bx - ax, by - ay
        den = dx * ey - dy * ex
        if abs(den) < 1e-12:
            continue
        t = ((ax - ox) * ey - (ay - oy) * ex) / den
        u = ((ax - ox) * dy - (ay - oy) * dx) / den
        if t > 0 and -1e-9 <= u <= 1 + 1e-9 and (best is None or t < best):
            best = t
    return best


def polar(points, origin, samples=720, smooth=7.0):
    """The polygon's distance from origin as a function of the angle (sampled, its pixel steps smoothed away over
    about smooth degrees, interpolated)."""
    raw = [ray_to_polygon(points, origin, 2 * math.pi * i / samples) for i in range(samples)]
    sigma = smooth / 360.0 * samples
    reach = int(3 * sigma)
    weights = [math.exp(-d * d / (2 * sigma * sigma)) for d in range(-reach, reach + 1)]
    table = [sum(w * raw[(i + d) % samples] for w, d in zip(weights, range(-reach, reach + 1))) / sum(weights)
             for i in range(samples)]

    def radius(phi):
        f = (phi % (2 * math.pi)) / (2 * math.pi) * samples
        i = int(f) % samples
        a = f - int(f)
        return table[i] * (1 - a) + table[(i + 1) % samples] * a
    return radius


def build_blast(colour):
    """The whole blast: [dome, core]."""
    outline = blast_outline(colour)
    centre_radius = polar(outline, (0.0, 0.0))

    def top(x, y):
        r = math.hypot(x, y)
        if r < 1e-9:
            return BLAST_HEIGHT
        rho = r / centre_radius(math.atan2(y, x))
        return BLAST_HEIGHT * max(0.0, 1.0 - rho * rho) ** 0.5
    rim = kit.rim_curve(RIM)

    def heat(u, phi):
        start = 1.0 - rim(phi)
        if u <= start:
            return WHITE
        f = min((u - start) / (1.0 - start), 1.0)
        return WHITE - (WHITE - RIM_HEAT) * f ** FALL
    many, reach, fade, base = TONGUES

    def waves(i, phi, u):
        down = abs(((math.degrees(phi) - 270.0) + 180.0) % 360.0 - 180.0)  # (degrees from straight down)
        strength = reach * max(0.0, 1.0 - down / fade) ** 1.2 + base
        return strength * math.sin(many * phi + 1.7 * i)
    bands = BLAST_BANDS[colour]
    dome = kit.Dome(BLAST_HOT, polar(outline, BLAST_HOT), top, heat, bands, segments=78, gap=0.12, waves=waves,
                    middle_fractions=(0.3, 0.6), rim_fractions=(0.35, 0.65, 0.85, 0.96, 1.0))
    mats = kit.materials("megacannon_blast_%s" % colour, bands)
    parts = [dome.build("megacannon_blast_%s" % colour, mats)]
    cx, cy, rx, ry, lift = BLAST_CORE
    cbands = BLAST_CORE_BANDS[colour]
    cmats = kit.materials("megacannon_core_%s" % colour, cbands, kit.CORE_ROUGHNESS)
    parts.append(kit.dome_core("megacannon_blast_core_%s" % colour, (cx, cy), rx, ry, lift, top, cbands, cmats,
                               segments=28, tongues=(5, 0.0, 1.0)))
    return parts


def pieces(colour, whole):
    """The blast cut into its four sprites' pieces, each moved onto its sprite's centre: {sprite: [objects]}."""
    cap = kit.materials("megacannon_core_%s" % colour, BLAST_CORE_BANDS[colour], kit.CORE_ROUGHNESS)[0]
    out = {}
    for sprite, box in PIECES[colour]:
        cx, cy = (box[0] + box[1]) / 2, (box[2] + box[3]) / 2
        parts = []
        for obj in whole:
            piece = mk.cut(obj, box, cap)
            if piece is None:
                continue
            piece.data.transform(Matrix.Translation((-cx, -cy, 0.0)))
            piece.name = "%s_b%d" % (obj.name, sprite)
            parts.append(piece)
        out[sprite] = parts
    return out


def build():
    options = k.args()
    only = set(options["only"].split(",")) if "only" in options else None
    outdir = options.get("outdir", kit.OUTDIR)
    sheets = options.get("check")
    for name, sprite, colour in (("shot_megacannon", 65, "blue"), ("shot_megacannon_2", 64, "fire")):
        if only is not None and name not in only:
            continue
        k.reset()
        parts = triangulate(kit.build_drop(name, DROP, "megacannon_" + colour, DROP_BANDS[colour],
                                           DROP_CORE_BANDS[colour]))
        bpy.context.view_layer.update()
        print(f"== {name} (shots {sprite}): a drop of plasma ({colour})")
        if sheets:
            kit.check_lines(name, parts, os.path.join(sheets, "shots.png"), [(sprite, 0, 0, 0)], (0.0, 3.5))
        bpy.context.scene.view_settings.view_transform = "Standard"
        mk.report(name, parts, os.path.join(outdir, name + ".glb"))
        if "preview" in options:
            view(options["preview"] + name, parts)
    for colour in ("blue", "yellow"):
        names = ["shot_megacannon_b%d" % s for s, _ in PIECES[colour]]
        if only is not None and not any(n in only for n in names):
            continue
        k.reset()
        whole = triangulate(build_blast(colour))
        bpy.context.view_layer.update()
        print("whole blast (%s): %d triangles, height %.2f" % (colour, mk.triangles(whole),
                                                              max(v.co.z for o in whole for v in o.data.vertices)))
        if sheets:
            sprites = [s for s, _ in PIECES[colour]]
            m = [a + b for a, b in zip(k.sprite_mask(os.path.join(sheets, "shots2.png"), sprites[0], large=False),
                                       k.sprite_mask(os.path.join(sheets, "shots2.png"), sprites[1], large=False))]
            m += [a + b for a, b in zip(k.sprite_mask(os.path.join(sheets, "shots2.png"), sprites[2], large=False),
                                        k.sprite_mask(os.path.join(sheets, "shots2.png"), sprites[3], large=False))]
            mk.compare("whole blast (%s)" % colour, mk.coverage(whole, 24, 28), m)
        if "preview" in options:
            bpy.context.scene.view_settings.view_transform = "Standard"
            view(options["preview"] + "shot_megacannon_%s_whole" % colour, whole, size=(24, 28))
        cut = pieces(colour, whole)
        for o in whole + [o for parts in cut.values() for o in parts]:
            o.hide_render = True
        for sprite, parts in cut.items():
            name = "shot_megacannon_b%d" % sprite
            if only is not None and name not in only:
                continue
            for o in parts:
                o.hide_render = False
            if sheets:
                mk.compare("%s (shots2 %d)" % (name, sprite), mk.coverage(parts, 12, 14),
                           k.sprite_mask(os.path.join(sheets, "shots2.png"), sprite, large=False))
            bpy.context.scene.view_settings.view_transform = "Standard"
            mk.report(name, parts, os.path.join(outdir, name + ".glb"))
            if "preview" in options:
                view(options["preview"] + name, parts)
            for o in parts:
                o.hide_render = True


if __name__ == "__main__":
    build()
