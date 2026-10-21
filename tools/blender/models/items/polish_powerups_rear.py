"""The rear weapon pick-ups of the power-ups sheet ("twoplayer" in the catalogue; values 31009-31022, the weapon
port they give; 2x2 sprites, 24 x 28 pixels, one frame each; dropped by enemies in every episode, 191, 193 and 199 also
placed on the ground in episode 1), polished (2026-10-21; they replace powerups_rear.py's models): a red orb, the front
weapons' orb (polish_powerups_front.orb) in ramp 4, with the weapon's symbol on its face. models.cfg: model pu_<name>
items/pu_<name>.glb and sprite powerups <n> pu_<name> yaw=0, unchanged (no spin: the orb is painted for the camera,
as the front weapons' is).

- pu_starburst (169): two four-pointed stars of fire, white-hot in their hearts (Starburst)
- pu_multi_rear (191): three tongues of fire hanging from a dark crown, glowing at their round ends (Multi-Cannon,
  rear)
- pu_sonic_wave (193): a green crescent with two nested ridges round a dark groove, a sound wave (Sonic Wave)
- pu_protron_rear (195): four blue cushion gems in a diamond, in a dark socket (Protron, rear)
- pu_wild_ball (197): a green glass ball in a steel cradle of two lobes (Wild Ball)
- pu_vulcan_rear (199): two bullets flying up and out, their noses hot (Vulcan Cannon, rear)
- pu_heavy_missile_rear (243): steel pods swept up and out, red lamps glowing between them and the inner pods, on a
  green mount (Rear Heavy Missile Launcher)
- pu_mega_pulse_rear (245): a red horn, its bell a glowing ring round a dark hollow with a spark in it, its tail swept
  to the right (Rear Mega Pulse)

No symbol is another sprite's pixels mirrored, turned or in other ramps (each checked against every sprite of the
sheet, shifted, mirrored and turned: the best other match, 191 against 155's winged badge upside down, shares 63 % of
its shades). Inside the sprites: 169's right star is its left star moved (10, -1); 191, 193, 199 and 243 are
symmetric about x = 0, 245 about y = 0; 195's four gems are one gem repeated: the models build them so. No other
enemy shows these sprites (no frame models).

The orb is polish_powerups_front.orb(4), imported (the front weapons', the rear weapons' and the sidekicks' orbs are
one picture shade for shade in ramps 13, 4 and 2): glossy glazed ice of shade 0x48 glowing faintly in 0x49, its rim
0x47 and 0x45, the cross of grooves 0x42, the gathered light 0x4b and 0x4d inside its lower right.

The symbols are made as the front weapons' are: reliefs (polish_powerups_front.relief()) raised over the ball's dome
from the sprites' outlines (2D signed distance fields: circles, ellipses, boxes, polygons, capsules and convex hulls,
joined, cut, turned and rounded), each on a dark setting in its sprite's outline colour, painted in bands (paint()):
by depth, by a field of the shape's own (a star's own measure, a flame's glow drawn out along it from its round end, a
bullet's hot stripe along its length) or up the screen (the sonic wave's ridges lighter downwards, the cradle's lip
and fold). 243's pods are lathed capsules bent with the dome, as the front's rockets. Glows 0.1-0.6 in their own
palette colours (the game's bloom adds); at most 14 materials per model.

Built in view space (the game camera's view, the sprite its top view) and tilted into the game's axes with
polish_powerups_front.to_world(), so that every symbol shows where the sprite draws it from the game's camera (from
straight above it sits about 3 pixels lower on the ball). Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right,
+Y up the screen, +Z towards the camera; origin at the sprite's centre (pixel 12, 14); column c is x = c + 0.5 - 12,
row r is y = 13.5 - r. The game centres the models in height on their layer.

Replaces powerups_rear.py (all of it: ICON_191, ICON_193, ICON_243, ICON_245, the eight builders, MODELS), and with
it the last models of powerups.py and powerups_parts.py (the sidekicks have moved to polish_powerups_sidekicks.py):
all three go. Imports only polish_powerups_front and polish_item_kit.

Options after "--": --outdir <dir> (default assets/models/items), --check <sheets dir or powerups.png> (each model's
silhouette as the game's camera sees it and from straight above against its sprite, and its symbol alone against the
sprite's pixels that are not the orb's), --preview <prefix> (top and 3/4 views), --only <name,...>.
"""
import math
import os
import sys

import bpy
import numpy as np
from mathutils import Matrix

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polish_item_kit as kit  # noqa: E402
from polish_item_kit import k  # noqa: E402
import polish_powerups_front as front  # noqa: E402
from polish_powerups_front import (blend, box, capsule, circle, depth_of, dome, ellipse, exact, glowing,  # noqa: E402
                                   grow, intersect, material, minus, mirror_half, paint, polygon, relief,
                                   round_profile, rounded, union)

ORB_RAMP = 4    # flesh red: the rear weapons' orb


# --- Shape helpers (with polish_powerups_front's fields) ----------------------------------------------------------

def turned(f, degrees, cx=0.0, cy=0.0):
    """A shape (or any field of x and y) turned counter-clockwise by degrees about (cx, cy)."""
    a = math.radians(degrees)
    c, s = math.cos(a), math.sin(a)

    def g(x, y):
        x = np.asarray(x, float) - cx
        y = np.asarray(y, float) - cy
        return f(c * x + s * y + cx, -s * x + c * y + cy)
    return g


def half_plane(side, offset=0.0):
    """x * side > offset (inside < 0)."""
    return lambda x, y: offset - side * np.asarray(x, float)


def ridge_profile(width, height, steps=6, power=1.0, edge=0.25):
    """An edge rising over width from the outline in to a crest, height high: straight (power 1) or fuller
    (power < 1), its foot rounded over `edge`."""
    out = []
    for i in range(steps + 1):
        t = i / steps
        d = width * t
        under = height * (1.0 - t) ** (1.0 / power) if power != 1.0 else height * (1.0 - t)
        out.append((d, under))
    if edge > 0:
        out.insert(1, (edge * 0.35, height - edge * 0.55))
    return out


# --- Starburst: two four-pointed stars of fire -------------------------------------------------------------------
# The sprite's two stars (hearts at column 7, row 13 and column 17, row 14: one star moved; points reaching 5 pixels
# across and 6 up and down, the upright points three pixels wide, the level ones one), white-yellow in their hearts
# (0x7e) through yellow and orange to red at their points (0x74, 0x70), their dark outlines (0x41, 0x43, 0x10) joined
# between them: stars of glowing fire, ridged along their points (the depth's profile), painted in their own measure
# (scaled copies of the star) from the white heart out, on one dark setting.

STARS = [(-4.5, 0.5), (5.5, -0.5)]      # their hearts (columns 7 and 17, rows 13 and 14)
STAR_REACH = (5.6, 6.6)                 # how far their points reach across and up
STAR_POWER = 0.53                       # the curve of their sides (1 straight, smaller thinner points)
STAR_STEM = (1.4, 5.6)                  # the fuller upright points (the sprite's three-pixel stem)
STAR_BANDS = [0.16, 0.34, 0.52, 0.72]   # the colour bands' borders in the star's own measure
STAR_COLOURS = [(0x7f, 0x7f, 0.6), (0x7d, 0x7d, 0.54), (0x7a, 0x7b, 0.48), (0x78, 0x79, 0.42), (0x75, 0x76, 0.36)]


def star_measure(cx, cy):
    """A star's own measure: 0 in its heart, 1 on its outline, the stars between scaled copies of it."""
    a, b = STAR_REACH

    def f(x, y):
        u = np.abs((np.asarray(x, float) - cx) / a)
        v = np.abs((np.asarray(y, float) - cy) / b)
        return (u ** STAR_POWER + v ** STAR_POWER) ** (1.0 / STAR_POWER)
    return f


def star_shape(cx, cy):
    m = star_measure(cx, cy)
    return blend(lambda x, y: (m(x, y) - 1.0) * 4.0, ellipse(cx, cy, *STAR_STEM), 0.5)


def starburst():
    """169: two stars of fire."""
    setting = material("star_setting", 0x41, 0.3, 0.3)
    mats = [glowing(f"star{i}", index, glow, strength, 0.0, 0.3) for i, (index, glow, strength) in
            enumerate(STAR_COLOURS)]
    shapes = [rounded(star_shape(x, y), 0.15, 0.3) for x, y in STARS]
    parts = [relief("star_setting", rounded(union(*[grow(s, 0.72) for s in shapes]), 0.0, 0.5), 0.4, setting,
                    bevel=0.3, segments=2, inner=0, hollow=1.6)]
    for i, ((x, y), shape) in enumerate(zip(STARS, shapes)):
        obj = relief(f"star{i}", shape, 2.6, mats[-1], profile=ridge_profile(2.1, 2.2, 9), inner=0, spacing=0.3)
        m = star_measure(x, y)
        paint(obj, lambda xs, ys, zs, m=m: m(xs, ys), STAR_BANDS, mats)
        parts.append(obj)
    return parts


# --- Multi-Cannon (rear): three tongues of fire -------------------------------------------------------------------
# The sprite's three flames pouring down (the middle one upright, columns 10-13, rows 9-19; the side ones leaning in
# at their tops, columns 4-9, rows 7-17), each round below and pointed above, dark red at its point (0x72), glowing
# yellow in its round end (0x7c), under a dark crown between their points (0x10, 0x40): tongues of fire on a dark
# setting, their glow drawn out along each flame from a hot spot in its round end.

# Each flame: its round end's middle and radius, its point, and its radius `taper` pixels before the point.
FLAMES = [((-6.0, -1.9), 2.15, (-2.4, 7.3), 1.35, 3.0), ((0.0, -3.85), 2.15, (0.0, 5.7), 1.4, 3.0),
          ((6.0, -1.9), 2.15, (2.4, 7.3), 1.35, 3.0)]
FLAME_CROWN = [(-2.9, 7.7), (2.9, 7.7), (1.6, 4.2), (-1.6, 4.2)]   # the dark between the points
FLAME_STRETCH = 1.8                  # the glow's bands drawn out along the flame
FLAME_HOT = [0.95, 1.9, 2.9, 4.1]    # their borders (pixels across the flame) from the hot spot out


def hull(points):
    """The convex hull of points, counter-clockwise (monotone chain)."""
    pts = sorted(set(points))

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lower, upper = [], []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    return lower[:-1] + upper[:-1]


def tapered(end, r0, tip, r1, taper, steps=36):
    """A tongue of fire or a bullet: round about `end` (radius r0), narrowing straight to radius r1 `taper` pixels
    before `tip`, then drawn to a point at tip (the hull of the two circles and the point)."""
    ux, uy, length = axis_frame(end, tip)
    mx, my = tip[0] - ux * taper, tip[1] - uy * taper
    pts = [tip]
    for cx, cy, r in ((end[0], end[1], r0), (mx, my, r1)):
        pts += [(round(cx + r * math.cos(2 * math.pi * i / steps), 6), round(cy + r * math.sin(2 * math.pi * i / steps),
                                                                              6)) for i in range(steps)]
    return polygon(hull(pts))


def axis_frame(end, tip):
    """(ux, uy): the unit vector from end to tip, and the length."""
    length = math.hypot(tip[0] - end[0], tip[1] - end[1])
    return (tip[0] - end[0]) / length, (tip[1] - end[1]) / length, length


def multi_rear():
    """191: three tongues of fire."""
    setting = material("flame_setting", 0x41, 0.25, 0.5)
    fire = [glowing("flame_core", 0x7c, 0x7d, 0.58, 0.0, 0.25), glowing("flame_hot", 0x79, 0x7a, 0.48, 0.0, 0.25),
            glowing("flame_mid", 0x77, 0x78, 0.4, 0.0, 0.25), glowing("flame_red", 0x75, 0x76, 0.32, 0.0, 0.25),
            glowing("flame_dark", 0x73, 0x74, 0.26, 0.0, 0.25)]
    shapes = [rounded(tapered(*f), 0.3, 0.0) for f in FLAMES]
    crown = polygon(FLAME_CROWN)
    parts = [relief("flame_setting", rounded(union(crown, *[grow(s, 0.7) for s in shapes]), 0.0, 0.8), 0.4,
                    setting, bevel=0.3, segments=2, inner=1)]
    for i, ((end, r, tip, _, _), shape) in enumerate(zip(FLAMES, shapes)):
        obj = relief(f"flame{i}", shape, 2.5, fire[-1], profile=round_profile(1.9, 1.9, 6), inner=0, spacing=0.45)
        ux, uy, _ = axis_frame(end, tip)
        hx, hy = end[0] - ux * 0.3, end[1] - uy * 0.3
        depth = depth_of(shape)

        def hot(xs, ys, zs, depth=depth, hx=hx, hy=hy, ux=ux, uy=uy):
            along = ((xs - hx) * ux + (ys - hy) * uy) / FLAME_STRETCH
            across = (xs - hx) * -uy + (ys - hy) * ux
            return np.where(depth(xs, ys, zs) > 0.4, -np.hypot(along, across), -99.0)
        paint(obj, hot, [-98.0] + [-b for b in reversed(FLAME_HOT)], [None] + fire[::-1])
        parts.append(obj)
    return parts


# --- Sonic Wave: a green crescent, a sound wave -------------------------------------------------------------------
# The sprite's green crescent (columns 7-16, rows 8-20: two horns two pixels wide, a V cut between them down to row
# 12, round below), dark at its edges (0xc0-0xc2), a darker V inside it (the groove: column 8 down to row 13, then
# to the middle of row 16) between a lighter inner band (0xc9-0xcc) and a bright outer one (0xcc-0xcf at the bottom,
# 0xc3-0xc6 in the horns): a dark green crescent with two raised rounded ridges along it, the outer one running up the
# horns, the inner one in the V, lighter downwards.

WAVE_INNER = [(0.0, 1.05), (1.0, 1.5), (2.0, 2.45), (2.7, 3.45), (2.75, 4.75), (3.35, 5.6), (4.1, 6.1)]
WAVE_OUTER = [(4.95, 5.8), (5.2, 4.6), (5.2, 2.0), (5.1, -1.4), (4.7, -3.2), (4.1, -4.8), (3.1, -6.0),
              (1.9, -6.8), (0.0, -7.1)]
WAVE_GROOVE = [(2.5, 8.0), (2.5, 3.5), (3.4, 2.3), (3.4, 0.6), (2.6, -0.6), (1.6, -1.6), (0.6, -2.3), (0.0, -2.45)]
WAVE_INSET = 0.3        # the dark rim of the crescent showing round the ridges


def sonic_wave():
    """193: a green crescent with two nested ridges."""
    base_mat = glowing("wave_base", 0xc2, 0xc3, 0.1, 0.1, 0.3)
    green = [glowing("wave0", 0xc5, 0xc6, 0.16, 0.1, 0.18), glowing("wave1", 0xc8, 0xc9, 0.24, 0.1, 0.18),
             glowing("wave2", 0xcb, 0xcc, 0.32, 0.1, 0.18), glowing("wave3", 0xce, 0xcf, 0.42, 0.1, 0.18)]
    crescent = rounded(polygon(mirror_half(WAVE_INNER + WAVE_OUTER)), 0.4, 0.6)
    notch = polygon(mirror_half(WAVE_GROOVE))
    band = grow(crescent, -WAVE_INSET)
    outer = rounded(minus(band, grow(notch, 0.3)), 0.3, 0.3)
    inner = rounded(intersect(band, grow(notch, -0.3), box(-8.0, 8.0, -8.0, 2.1)), 0.35, 0.3)
    parts = [relief("wave_base", crescent, 0.8, base_mat, bevel=0.3, segments=2, inner=2)]
    o = relief("wave_outer", outer, 2.2, green[0], profile=round_profile(0.75, 1.25, 6, power=1.3), inner=1,
               spacing=0.35)
    paint(o, lambda x, y, z: -y, [-1.5, 2.0, 4.6], green)
    i = relief("wave_inner", inner, 2.0, green[1], profile=round_profile(0.7, 1.15, 6, power=1.3), inner=1,
               spacing=0.35)
    paint(i, lambda x, y, z: -y, [0.0], green[1:3])
    return parts + [o, i]


# --- Protron (rear): four blue gems ------------------------------------------------------------------------------
# The sprite's four gems (one 6 x 4 pixel gem repeated: deep blue 0x93-0x9b with a pale 0x8b glint at its upper right,
# a dark outline 0x30, 0x32, 0x51, 0x63), in a diamond: domed cushions turned along the diamond (as the upscale), in a
# dark socket (0x63, the front Protron's), a lighter streak of light over each one's upper right.

GEMS = [(1.0, 5.0), (-3.0, 2.0), (3.0, 0.0), (-1.0, -3.0)]   # (columns 12.5, 8.5, 14.5, 10.5; rows 8.5-16.5)
GEM_HALF, GEM_CORNER, GEM_TURN = 2.3, 1.35, 36.0
GEM_STREAK = ((-0.45, 0.85), (0.75, 0.2), 0.3)   # the light's streak over each gem's upper right (from its middle)


def protron_rear():
    """195: four blue gems in a dark socket."""
    socket_mat = material("gem_socket", 0x63, 0.3, 0.3)
    blue = [glowing("gem0", 0x95, 0x96, 0.22, 0.15, 0.1), glowing("gem1", 0x99, 0x9a, 0.28, 0.15, 0.1),
            glowing("gem2", 0x9b, 0x9c, 0.34, 0.15, 0.1)]
    streak_mat = glowing("gem_streak", 0x9e, 0x9f, 0.42, 0.05, 0.08)
    shapes = [turned(box(x - GEM_HALF, x + GEM_HALF, y - GEM_HALF, y + GEM_HALF, GEM_CORNER), GEM_TURN, x, y)
              for x, y in GEMS]
    socket = rounded(union(*[grow(s, 0.7) for s in shapes]), 0.0, 0.8)
    parts = [relief("gem_socket", socket, 0.5, socket_mat, bevel=0.3, segments=2, inner=1)]
    (ax, ay), (bx, by), sr = GEM_STREAK
    for i, ((x, y), shape) in enumerate(zip(GEMS, shapes)):
        obj = relief(f"gem{i}", shape, 2.8, blue[0], profile=round_profile(2.1, 2.2, 8), inner=2,
                     spacing=0.3)
        paint(obj, depth_of(shape), [0.45, 1.3], blue)
        streak = capsule(x + ax, y + ay, x + bx, y + by, sr)
        paint(obj, lambda xs, ys, zs, streak=streak: -streak(xs, ys), [0.0], [None, streak_mat])
        parts.append(obj)
    return parts


# --- Wild Ball: a green glass ball in a steel cradle --------------------------------------------------------------
# The sprite's green ball (columns 7-17, rows 6-15, round (0.5, 3)), its white glint and light (0x2f, 0xcd-0xcf) in its
# upper middle, its lower half dark (0xc0-0xc4) with light gathering in its lower right (0xc8-0xcc), resting in a
# cradle of two steel-blue lobes (columns 2-21, rows 10-20, a notch between them at the bottom; 0x34-0x3f: lit at the
# upper left, a darker fold across them, a light lip along their lower edges), outlined dark (0x30, 0x20-0x22): a domed
# glass ball over two pillows of steel.

BALL = (0.5, 3.0, 4.85, 4.45)
CRADLE = [(0.0, 4.2), (6.4, 4.2), (7.5, 3.3), (8.6, 2.3), (9.6, 1.0), (10.0, -0.4), (10.0, -3.6), (9.5, -4.8),
          (8.4, -6.1), (7.0, -6.9), (5.0, -7.05), (3.1, -6.9), (1.9, -6.3), (1.15, -5.4), (0.0, -4.95)]
CRADLE_BOTTOM = (-7.0, 4.6, 0.1)   # each lobe's lower edge: y = a + c (x -/+ b)^2
CRADLE_BANDS = [1.55, 2.85]        # the lip and the fold above it, measured up from that edge


def wild_ball():
    """197: a green glass ball in a steel cradle."""
    setting = material("cradle_setting", 0x30, 0.3, 0.3)
    steel = [material("cradle_top", 0x3b, 0.45, 0.25), material("cradle_fold", 0x38, 0.45, 0.28),
             material("cradle_lip", 0x3d, 0.45, 0.22)]
    green = [glowing("ball_rim", 0xc3, 0xc4, 0.18, 0.1, 0.08), glowing("ball", 0xc6, 0xc7, 0.22, 0.1, 0.08),
             glowing("ball_light", 0xca, 0xcb, 0.3, 0.1, 0.08), glowing("ball_core", 0xce, 0xcf, 0.4, 0.1, 0.08)]
    bx, by, rx, ry = BALL
    ball = ellipse(bx, by, rx, ry)
    cradle = rounded(polygon(mirror_half(CRADLE)), 0.3, 0.6)
    parts = [relief("cradle_setting", rounded(union(cradle, grow(ball, 0.7)), 0.0, 0.6), 0.4, setting, bevel=0.3,
                    segments=2, inner=1)]
    for side in (-1, 1):
        lobe = rounded(intersect(grow(cradle, -0.7), half_plane(side, 0.18)), 0.4, 0.0)
        obj = relief(f"cradle{side + 1}", lobe, 2.3, steel[0], profile=round_profile(3.2, 2.4, 8), inner=3,
                     spacing=0.5)

        def over_bottom(x, y, z, side=side):
            # How far above the lobe's lower edge (the sprite's light lip in rows 18-19, the darker fold above).
            return y - (CRADLE_BOTTOM[0] + CRADLE_BOTTOM[2] * (x - side * CRADLE_BOTTOM[1]) ** 2)
        paint(obj, over_bottom, CRADLE_BANDS, [steel[2], steel[1], steel[0]])
        parts.append(obj)
    obj = relief("ball", exact(ball), 4.4, green[1], profile=round_profile(min(rx, ry) * 0.98, 4.0, 9), inner=0,
                 spacing=0.4)
    depth = depth_of(ball)
    paint(obj, lambda x, y, z: by - 0.2 - y, [0.0], [None, green[0]])
    paint(obj, depth, [0.55], [green[0], None])
    light = circle(bx - 1.0, by + 1.1, 2.3)
    core = circle(bx - 1.0, by + 1.25, 1.05)
    paint(obj, lambda x, y, z: -light(x, y), [0.0], [None, green[2]])
    paint(obj, lambda x, y, z: -core(x, y), [0.0], [None, green[3]])

    def caustic(x, y, z):
        u, v = (x - bx) / rx, (y - by) / ry
        rho = np.hypot(u, v)
        a = np.degrees(np.arctan2(v, u))
        t = ((a + 40.0 + 180.0) % 360.0 - 180.0) / 45.0
        return rho - 0.93 + 0.2 * np.maximum(0.0, 1.0 - t * t)
    paint(obj, caustic, [0.0], [None, green[2]])
    parts.append(obj)
    return parts


# --- Vulcan Cannon (rear): two bullets flying up and out ----------------------------------------------------------
# The sprite's two bullets (columns 3-10 and 13-20, rows 8-19) leaning out at their noses, round and hot above
# (0x7b, 0x7c), straight, tapering to a point at their tails (0x72), on a dark outline (0x40, 0x10, 0x41): the front
# Vulcan's bullets turned out (its materials, its hot stripe from tail to nose), on a dark setting.

# Each bullet (with its setting): its round nose's middle and radius, its tail's point, its radius `taper` pixels
# before the point.
VULCAN_REAR = [((-6.5, 3.4), 2.65, (-2.45, -6.2), 1.95, 3.2), ((6.5, 3.4), 2.65, (2.45, -6.2), 1.95, 3.2)]
VULCAN_STRIPE = [0.42, 0.74]    # the hot stripe's tail, middle and nose, in parts of the length from the tail


def vulcan_rear():
    """199: two bullets flying up and out, their noses hot."""
    setting = material("bullet_setting", 0x41, 0.3, 0.3)
    body = [glowing("bullet0", 0x74, 0x75, 0.22, 0.3, 0.22), glowing("bullet1", 0x77, 0x78, 0.3, 0.3, 0.22)]
    stripe = [glowing("bullet_tail", 0x76, 0x77, 0.38, 0.2, 0.2), glowing("bullet_mid", 0x79, 0x7a, 0.46, 0.2, 0.2),
              glowing("bullet_nose", 0x7c, 0x7d, 0.58, 0.2, 0.2)]
    shapes = [rounded(tapered(*v), 0.3, 0.0) for v in VULCAN_REAR]
    parts = [relief("bullet_setting", rounded(union(*shapes), 0.0, 0.4), 0.45, setting, bevel=0.3, segments=2,
                    inner=1)]
    for i, ((nose, r, tail, _, _), shape) in enumerate(zip(VULCAN_REAR, shapes)):
        b = grow(shape, -0.7)
        obj = relief(f"bullet{i}", b, 2.5, body[0], profile=round_profile(1.8, 1.9, 6), inner=0, spacing=0.5)
        depth = depth_of(b)
        paint(obj, depth, [0.55], body)
        ux, uy, length = axis_frame(tail, nose)
        length += r

        def along(xs, ys, zs, depth=depth, tail=tail, ux=ux, uy=uy, length=length):
            s = ((xs - tail[0]) * ux + (ys - tail[1]) * uy) / length
            return np.where(depth(xs, ys, zs) > 0.65, s, -99.0)
        paint(obj, along, [-98.0] + VULCAN_STRIPE, [None] + stripe)
        parts.append(obj)
    return parts


# --- Rear Heavy Missile Launcher: steel pods with red lamps on a green mount ------------------------------------
# The sprite's two arms swept up and out (reaching a pixel past the ball at columns 1 and 22), each a steel block at
# its outer end (0x34-0x3e), a red lamp (0x73-0x7b) and a smaller steel piece (0x36-0x3b, a 0x1e glint), over a green
# mount at the bottom (0x22-0x26: two lobes and a stem between them), outlined dark (0x01, 0x20, 0x31, 0x50): lathed
# steel capsules, domed glowing lamps with hot hearts and a green mount, on a dark setting, as the upscale draws them.

# The left half (the right one mirrored): the outer steel pod (the sprite's block, rows 8-12, columns 1-6), the red
# lamp (rows 12-15, columns 5-8), the inner steel pod (rows 14-17, columns 7-10), the green mount below them (its
# lobes in rows 18-19, its stem in columns 11-12, rows 15-17).
POD_OUTER = ((-9.0, 3.9), (-6.4, 2.25), 2.15)       # the ends' middles and the radius
POD_INNER = ((-2.45, -0.75), (-3.75, -2.85), 1.35)
LAMP = (-5.0, 0.1, 1.95)
LAMP_HOT = (-5.0, -0.05, 1.0)
MOUNT = [(0.0, -0.5), (1.1, -0.6), (1.4, -1.5), (2.4, -2.6), (3.4, -3.5), (4.1, -4.3), (4.2, -5.2), (3.7, -6.0),
         (2.6, -6.25), (1.5, -6.0), (1.0, -5.2), (0.6, -4.4), (0.0, -4.25)]


def tube_body(name, profile, mat, start, angle, axis_z=0.9, squash=0.85, segments=28):
    """A lathed tube lying on the ball: profile (distance along its axis from start, radius), the axis turned
    angle degrees from +x, bent with the dome."""
    obj = k.lathe(name, profile, mat, segments, axis_x=0.0, axis_z=0.0, squash=squash)
    m = Matrix.Translation((start[0], start[1], 0.0)) @ Matrix.Rotation(math.radians(angle - 90.0), 4, "Z")
    obj.data.transform(m)
    for v in obj.data.vertices:
        v.co.z += dome(v.co.x, v.co.y) + axis_z
    obj.data.update()
    return k.smooth(obj, 50.0)


def pod(name, a, b, r, mat, axis_z=0.9, steps=6):
    """A lathed capsule lying on the ball from a to b (its ends' middles), r round."""
    ux, uy, length = axis_frame(a, b)
    cap = [math.pi / 2 * i / steps for i in range(steps + 1)]
    profile = ([(r * (1 - math.cos(q)), r * math.sin(q)) for q in cap] +
               [(length + r + r * math.sin(q), r * math.cos(q)) for q in cap[1:]])
    start = (a[0] - ux * r, a[1] - uy * r)
    return tube_body(name, profile, mat, start, math.degrees(math.atan2(uy, ux)), axis_z)


def heavy_missile_rear():
    """243: steel pods with red lamps swept up and out of a green mount."""
    setting = material("launcher_setting", 0x20, 0.3, 0.35)
    steel = [material("pod_steel", 0x3b, 0.35, 0.24), material("pod_light", 0x3c, 0.35, 0.22)]
    lamp_mats = [glowing("lamp_rim", 0x73, 0x74, 0.28, 0.2, 0.2), glowing("lamp", 0x75, 0x76, 0.38, 0.2, 0.18),
                 glowing("lamp_hot", 0x79, 0x7a, 0.5, 0.1, 0.18)]
    green = [material("mount", 0x24, 0.3, 0.26), material("mount_light", 0x26, 0.3, 0.24)]
    mount = rounded(polygon(mirror_half(MOUNT)), 0.3, 0.5)
    plans = [mount]
    pieces = []
    for side in (-1, 1):
        def at(p, side=side):
            return (p[0] * -side, p[1])
        (a, b, r), (c, d, q) = POD_OUTER, POD_INNER
        plans += [capsule(*at(a), *at(b), r), capsule(*at(c), *at(d), q)]
        pieces.append(pod(f"pod_outer{side + 1}", at(a), at(b), r, steel[0]))
        pieces.append(pod(f"pod_inner{side + 1}", at(c), at(d), q, steel[1], axis_z=1.1))
        lx, ly, lr = LAMP
        lx = lx * -side
        lamp = circle(lx, ly, lr)
        plans.append(lamp)
        obj = relief(f"lamp{side + 1}", lamp, 3.1, lamp_mats[1], profile=round_profile(lr * 0.95, 2.0, 7),
                     inner=0, spacing=0.35)
        paint(obj, depth_of(lamp), [0.4], [lamp_mats[0], None])
        hx, hy, hr = LAMP_HOT
        hot = circle(hx * -side, hy, hr)
        paint(obj, lambda x, y, z, hot=hot: -hot(x, y), [0.0], [None, lamp_mats[2]])
        pieces.append(obj)
    parts = [relief("launcher_setting", rounded(grow(union(*plans), 0.7), 0.0, 0.5), 0.4, setting, bevel=0.3,
                    segments=2, inner=1)]
    m = relief("mount", mount, 1.8, green[0], profile=round_profile(1.1, 1.3, 5), inner=1, spacing=0.4)
    paint(m, depth_of(mount), [0.65], green)
    return parts + [m] + pieces


# --- Rear Mega Pulse: a red horn with a glowing ring round a dark hollow ------------------------------------------
# The sprite's red horn (columns 5-17, rows 7-20): its bell round on the left, a ring of orange (0x76-0x79) round a
# dark hollow (0x70, columns 8-11, rows 11-16) with a yellow spark in its upper left (0x7c, column 9, row 12), its
# tail swept to the right (0x71-0x75, its end cut in points at rows 10, 13-14 and 17), outlined dark (0x10, 0x40,
# 0x70, 0xa1): a red cushion with a raised glowing ring round a sunk dark hollow, a glowing spark in it.

PULSE_BELL = (-2.0, 0.0, 5.0, 7.0)
PULSE_TAIL = [(-1.0, 6.6), (2.0, 5.9), (4.5, 5.0), (6.1, 4.1), (5.4, 2.6), (5.3, 1.4), (6.0, 0.2), (6.0, -0.4),
              (5.3, -1.6), (5.4, -2.8), (6.1, -4.1), (4.5, -5.0), (2.0, -5.9), (-1.0, -6.6)]
PULSE_RING = (-1.75, 0.0, 3.6, 5.15)
PULSE_HOLLOW = (-2.0, 0.0, 2.05, 3.1)
PULSE_SPARK = (-2.2, 1.2, 0.85)


def mega_pulse_rear():
    """245: a red horn with a glowing ring round a dark hollow, a spark in it."""
    setting = material("pulse_setting", 0x70, 0.3, 0.3)
    body = [glowing("pulse_body", 0x73, 0x74, 0.26, 0.2, 0.26), glowing("pulse_body_light", 0x75, 0x76, 0.32,
                                                                          0.2, 0.26)]
    ring = [glowing("pulse_ring", 0x75, 0x76, 0.34, 0.1, 0.22), glowing("pulse_ring_crest", 0x78, 0x79, 0.44, 0.1,
                                                                          0.22)]
    hollow_mat = material("pulse_hollow", 0x71, 0.2, 0.4)
    spark = [glowing("pulse_spark", 0x7c, 0x7d, 0.55, 0.0, 0.2), glowing("pulse_spark_core", 0x7e, 0x7e, 0.6, 0.0,
                                                                          0.2)]
    outline = rounded(union(ellipse(*PULSE_BELL), polygon(PULSE_TAIL)), 0.35, 0.5)
    hollow = exact(ellipse(*PULSE_HOLLOW))
    ring_shape = minus(exact(ellipse(*PULSE_RING)), hollow)
    parts = [relief("pulse_setting", outline, 0.4, setting, bevel=0.3, segments=2, inner=0, hollow=1.6)]
    b = relief("pulse_body", minus(grow(outline, -0.7), grow(hollow, 0.3)), 1.6, body[0],
               profile=round_profile(1.6, 1.1, 5), inner=2, spacing=0.5)
    paint(b, lambda x, y, z: np.where(x > 0.8, 0.9 - np.abs(y), -1.0), [0.0], [None, body[1]])
    r = relief("pulse_ring", ring_shape, 2.6, ring[0], profile=round_profile(0.7, 1.0, 5), inner=0, spacing=0.3)
    paint(r, depth_of(ring_shape), [0.45], ring)
    h = relief("pulse_hollow", grow(hollow, 0.35), 0.7, hollow_mat, bevel=0.2, segments=2, inner=2)
    sx, sy, sr = PULSE_SPARK
    s = relief("pulse_spark", circle(sx, sy, sr), 1.5, spark[0], profile=round_profile(sr * 0.95, 0.7, 5), inner=0,
               spacing=0.3)
    paint(s, lambda x, y, z: -np.hypot(x - sx + 0.15, y - sy - 0.15), [-0.45], [spark[0], spark[1]])
    return parts + [b, r, h, s]


MODELS = {
    "pu_starburst": (169, starburst),
    "pu_multi_rear": (191, multi_rear),
    "pu_sonic_wave": (193, sonic_wave),
    "pu_protron_rear": (195, protron_rear),
    "pu_wild_ball": (197, wild_ball),
    "pu_vulcan_rear": (199, vulcan_rear),
    "pu_heavy_missile_rear": (243, heavy_missile_rear),
    "pu_mega_pulse_rear": (245, mega_pulse_rear),
}


# --- Building ----------------------------------------------------------------------------------------------------

_BASE = {}


def orb_picture(sheet):
    """The orb's own picture: each pixel's shade, the most common among the sheet's orb sprites (in their own
    ramps: 13 the front weapons, 4 the rear ones, 2 the sidekicks)."""
    if sheet in _BASE:
        return _BASE[sheet]
    sys.path.insert(0, os.path.join(HERE, "..", ".."))
    from sprite_profile import sprite_indices
    ramps = {n: 13 for n in (153, 155, 157, 159, 161, 163, 165, 167, 201, 203, 267, 269)}
    ramps.update({n: 4 for n in (169, 191, 193, 195, 197, 199, 243, 245)})
    ramps.update({n: 2 for n in (205, 207, 229, 231, 233, 235, 237, 239, 241, 281)})
    counts = {}
    for n, ramp in sorted(ramps.items()):
        for y, row in enumerate(sprite_indices(sheet, n)):
            for x, v in enumerate(row):
                if v is not None and v >> 4 == ramp:
                    c = counts.setdefault((x, y), {})
                    c[v & 15] = c.get(v & 15, 0) + 1
    _BASE[sheet] = {p: max(sorted(c), key=lambda s: c[s]) for p, c in counts.items()}
    return _BASE[sheet]


def symbol_mask(sheet, sprite):
    """The symbol's pixels: those that are not the orb's own picture in ramp 4."""
    sys.path.insert(0, os.path.join(HERE, "..", ".."))
    from sprite_profile import sprite_indices
    base = orb_picture(sheet)
    return [[v is not None and not ((x, y) in base and v == 16 * ORB_RAMP + base[(x, y)]) for x, v in enumerate(row)]
            for y, row in enumerate(sprite_indices(sheet, sprite))]


def check_symbol(opts, name, sprite, objects):
    """The symbol alone (the orb left out) as the game's camera sees it, against the sprite's pixels that are not
    the orb's."""
    if "check" not in opts:
        return None
    mask = symbol_mask(front.sheet_path(opts), sprite)
    return kit.compare("%s (powerups %d): the symbol as the game's camera sees it" % (name, sprite),
                       kit.coverage(objects, 24, 28), mask)


def build_model(name):
    """The model's parts in view space (the orb first)."""
    sprite, symbol = MODELS[name]
    k.reset()
    parts = [front.orb(ORB_RAMP)] + [p for p in symbol() if p is not None]
    for obj in parts:
        kit.drop_unused_materials(obj)
    return sprite, parts


def build():
    opts = kit.options()
    for name in MODELS:
        if not kit.wanted(opts, name):
            continue
        sprite, parts = build_model(name)
        front.triangulate(parts)
        front.check_view(opts, name, sprite, parts)
        check_symbol(opts, name, sprite, parts[1:])
        front.to_world(parts)
        front.check_top(opts, name, sprite, parts)
        bpy.context.scene.view_settings.view_transform = "Standard"
        kit.report(name, parts, os.path.join(kit.outdir(opts), name + ".glb"))
        if "preview" in opts:
            kit.preview(opts["preview"] + name, parts, (24, 28), scale=16, distance=0.6)


if __name__ == "__main__":
    build()
