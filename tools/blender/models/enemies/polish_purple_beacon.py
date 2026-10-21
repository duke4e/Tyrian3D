"""HARVEST's purple machine (sheet 5 sprite 3, 2x2: 24 x 26 pixels in the 24 x 28 cell; sky and top layers; enemy 73
of episode 4, 24 of them in HARVEST; its animation 3, 5, 5, 7, 7, ... 17, 17), polished (2026-10-21; it replaces
wave3_l.py's purple_beacon(), regions of the sprite's pixels inflated, tubes laid on). models.cfg: model
purple_beacon enemies/purple_beacon.glb (unchanged) and model purple_beacon_5 ... purple_beacon_17 (new); sprite 5 3
purple_beacon yaw=0 (unchanged); frame 5 5 purple_beacon_5 ... frame 5 17 purple_beacon_17. No other enemy (launched
ones included) shows sheet 5's sprites 3-17; none of them is another sprite's pixels mirrored, turned or in other
ramps; the sprite is its own mirror image about x = 0 (434 of its 441 pixels).

Its animation does not run by itself (animate 0), but HARVEST starts it 20 ticks after each machine appears (event
24: ani 15 from cycle 2), so the game shows frame 3 only at first, then loops 5, 5, 7, 7, ... 17, 17: every frame
after 3 lights the machine up (the slots three shades brighter, a green strip down each shoulder, columns 4 and 19
of rows 16-21, three green lights down the middle channel, rows 18, 20 and 22) and runs a bright green bar across
the block (columns 7-16) a row lower each frame, from row 18 (5) to row 24 (17).

As the sprite and its 4x upscale draw it (ramp 5 purples, ramp 12 greens, black outlines):
- at the top two lobes like horns (columns 6-11 and 12-17 of rows 0-5), a notch between their tips, a light ridge
  curving down each one's inner side, a crease between them;
- a neck (columns 8-15 of rows 6-9) down which the two ridges run together;
- the brow (rows 10-14): the neck flaring into a bar across, under it a dark visor (columns 9-14 of rows 12-13) lit
  at its upper corners (columns 10 and 13 of row 12), two eye pits at its ends (columns 9 and 14 of row 13, holes in
  the sprite);
- the shoulders (columns 0-5 and 18-23 of rows 10-21): broad plates falling away to the sides and down, their top
  edges dark, ribs down them (columns 2 and 4, 19 and 21), their lower edges stepping in to the block's foot;
- the block between them (columns 6-17 of rows 14-25), its top edge lit (row 15), its side walls lit (columns 6 and
  17) above the shoulders: two slots down its face (columns 7-8 and 15-16 of rows 16-25), green, a brighter spot near
  their tops, dark green at their feet; between them two ridges (columns 9-10 and 13-14) either side of a dark
  channel (columns 11-12).

Built as an organic body and a machined block. The body is one smooth solid over the machine's plan
(polish_ring_machine.relief(): a top over the plan, rounded down to its outline, straight walls, a flat underside):
the lobes, the neck, the brow and the shoulders a smooth union of caps, ridges and sloping plates (the shoulders
falling away outwards in a curve, a roll along their top edges, soft ribs down them), the ridges down the lobes and
the neck raised, the crease between the lobes, the visor and the eye pits sunk; under the block it is low. The block
stands on it as a CAD solid (polish_machine_kit): its plan extruded up to a top sloping down the screen (so its face
leans towards the game's camera), its edges bevelled, the slots and the channel cut down its face by exact booleans
(open at its foot, as the sprite draws them), the ridges rounded bars laid between them; the slots' floors glowing
plates in the cuts (dark green at their feet), a brighter lens near their tops; the channel's three lights small domes
on its floor; the lit rib down each shoulder's column 4 / 19 a rounded strip lying on it. Colours are the sprite's
indices, cut in along smooth borders on the body (the dark outline 0x51 along the plan's edges, the visor and the pits
0x51, the creases 0x53, the light crests 0x59 (the ridges down the head, the shoulders' rolls), the glints on the
visor's rim 0x5b, the shoulders below their rolls 0x55, the rest 0x57) and painted by how the faces meet the light on
the block (its top edge and left wall 0x59, its right and front walls and the slots' walls 0x55, the channel 0x53);
the slots' floors glow a little in their own colours (frame 3: 0xc4, the brighter lens 0xc8, the feet 0x24; well
under 1). The other frames are the same solids lit up: the slots 0xc7 / 0xcb / 0x27, the strips green (0xc6), the
channel's lights 0xcb / 0xc7 / 0x27 (the sprites' c7, c5, c2, brightest first; dark in frame 3), and the bar, a
glowing green ribbon (0xce, 0.6) lying across the block from column 7 to 16 over the ridges, down into the slots and
the channel, a pixel wide, at its frame's row. All frames reach from z 0 to 7.25 (the bar lies within), so the game,
which centres sky objects in height, keeps them in place.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera; origin at the
sprite's centre (pixel 12, 14); outlines are given in pixel edges: column c's left edge is x = c - 12, row r's top
edge y = 14 - r (px()). The machine is symmetric about x = 0.

Replaces wave3_l.py's purple_beacon(): remove its section ("# --- 5 3: HARVEST's purple machine" with its
@model("purple_beacon", 3) registration) and its line in the docstring, and wave3_l_art.py's BEACON (only
purple_beacon() reads it). Nothing imports wave3_l.py; its other models keep every import it has.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (each frame's silhouette
against its sprite in enemy_5.png), --preview <prefix>, --only <name,...>, --stats 1.
"""
import math
import os
import sys

import bmesh
import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
import polish_machine_kit as mk  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402
from polish_ring_machine import ccw, chaikin, relief, round_edge  # noqa: E402


def px(c, r):
    """A pixel edge point of the sprite, (column, row) from its top left corner, in model coordinates."""
    return (c - 12.0, 14.0 - r)


def mirror_plan(left):
    """A plan symmetric about x = 0 from its left half (from the top middle down to the bottom middle)."""
    pts = [px(c, r) for c, r in left]
    return pts + [(-x, y) for x, y in reversed(pts[1:-1])]


# --- The plan ---------------------------------------------------------------------------------------------------

# The machine's plan, its left half (column, row edges) from the notch between the lobes' tips round to the notch at
# the foot of the channel: the lobes, the neck, the shoulders' top edge and outer edge, their lower edge stepping in
# to the block's foot.
PLAN_LEFT = [(12.0, 1.0), (11.05, 0.95), (10.6, 0.25), (9.8, 0.0), (8.2, 0.0), (7.0, 0.5), (6.15, 1.4), (5.7, 2.6),
             (5.75, 3.9), (6.1, 5.0), (6.9, 5.8), (7.8, 6.2), (8.0, 7.0), (8.0, 8.5), (7.6, 9.25), (6.9, 9.75),
             (6.0, 10.0), (0.8, 10.0), (0.0, 10.75), (0.0, 20.6), (0.6, 21.3), (2.6, 22.25), (4.5, 23.2),
             (5.4, 24.2), (6.1, 25.3), (7.2, 26.0), (10.6, 26.0), (11.0, 25.5), (11.4, 25.05), (12.0, 25.0)]

# --- The organic body's heights ----------------------------------------------------------------------------------

EDGE_Z, EDGE_RIM = 1.0, 1.05        # the top at the plan's outline and how far in it rounds up to its full height
SHOULDER_RIM = 1.7                  # (farther on the shoulders' outer edges, |x| beyond 8)
BOTTOM = 0.0
BLEND = 1.1                         # the smooth union's reach
# The lobes: centre (x, y; mirrored), radii in plan, top.
LOBE = ((-3.0, 11.05), (3.25, 3.25), 6.7)
# The neck: a ridge down x = 0 from y0 to y1, its half-width and top.
NECK = (9.6, 2.6, 3.9, 5.6)
# The brow: across the middle (|x| under BROW_X, falling away beyond), its crest's y, its half-depth (y), top.
BROW = (2.1, 2.3, 6.0)
BROW_X = (5.0, 8.0)
# Under the block (|x| under 6, y under 0) the body is only as high as this (the block stands on it).
UNDER_BLOCK = 1.5
# The ridge down each lobe's inner side and the neck (x, y; mirrored), its height and half-width.
HORN = [(-3.75, 12.9), (-3.15, 11.2), (-2.35, 9.0), (-1.6, 6.8), (-1.15, 4.8), (-1.15, 3.3)]
HORN_H, HORN_W = 0.55, 0.62
# The crease between the lobes (x = 0, from y CREASE[0] up): depth, half-width.
CREASE = (3.2, 0.8, 0.6)
# The visor: centre, half-sizes, the power of its plan, depth; the eye pits (x, y; mirrored), radius, depth.
VISOR = ((0.0, 1.0), (2.75, 1.2), 2.2, 1.6)
PITS = ((-2.55, 0.45), 0.6, 2.4)
# The shoulders: their top at the brow's end (|x| 5.4, y SHOULDER_TOP), how far they fall to their outer edge (6.6
# pixels out) and how (the power of the curve), how much they fall per pixel down the screen; the roll along their
# top edge (its distance below it, half-width, height); the ribs down columns 2 and 4 (x, from y, to y, height,
# half-width; column 4's only above STRIP, which carries it on).
SHOULDER = (4.5, 2.6, 1.6, 0.1)
SHOULDER_TOP = 3.6
SHOULDER_ROLL = (1.25, 1.0, 0.55)
RIB2 = (-9.5, 1.6, -7.2, 0.45, 0.75)
RIB4 = (-7.5, 1.6, -2.4, 0.4, 0.7)
CREASE_SIDE = (6.0, 6.7)            # the dark crease where the shoulders meet the block's walls: |x| from, to

# --- The block ----------------------------------------------------------------------------------------------------

# Its plan (x from, to; y from, to; the corners' radii at its top and at its foot), its top (at y = 0) and slope
# (rising up the screen), the bevel of its edges.
BLOCK_PLAN = (-6.0, 6.0, -12.0, -0.35, 0.5, 1.4)
BLOCK_TOP = (5.35, 0.165)
BLOCK_BEVEL = 0.5
# The slots (|x| from, to; y from (past the block's foot: open there), to; corner radius, depth), the channel
# (half-width, y to, depth), the ridges between them (|x| middle, half-width, height over the top, y from, to).
SLOT = (3.0, 5.0, -13.0, -1.95, 0.85, 1.45)
CHANNEL = (0.95, -1.75, 0.95)
RIDGE = (2.0, 0.72, 0.36, -11.3, -2.25)
# The slots' glowing floors (their tops this far above the cut's floor), the feet (dark green below this y), the
# brighter spot near their tops (middle (|x|, y), radii, height).
FLOOR_LIFT, TIP_Y = 0.05, -10.35
HOT = ((4.15, -5.3), (0.8, 1.55), 0.16)
# The strip down column 4 (rows 16-21): x, from y, to y, half-width, height above the shoulder.
STRIP = (-7.5, -1.9, -8.15, 0.55, 0.32)
# The channel's three lights (rows 18, 20 and 22): y, radius, height.
DOTS = ((-4.5, -6.5, -8.5), 0.5, 0.42)
# The bar's rows (frames 5 ... 17: rows 18 ... 24), its half-width across the block, its width (y) and lift.
BAR_X, BAR_W, BAR_LIFT = 5.05, 0.92, 0.1

# The paint: the dark outline along the plan's edges (closer than this), the light crests (the ridges down the head,
# the shoulders' rolls: this close to their middle lines), the bright glints on the visor's upper rim (the sprite's
# 0x5d at columns 10 and 13 of row 12: centre (x, y; mirrored), radius), the block's lit top edge (above this y).
OUTLINE_D = 0.42
CREST = 0.3
ROLL_CREST = 0.5
GLINT = ((-1.85, 2.05), 0.42)
BLOCK_EDGE = -1.5

# The frames: model, sprite, the bar's row (None: no bar), whether the machine is lit up.
FRAMES = [("purple_beacon", 3, None, False)] + [("purple_beacon_%d" % s, s, 18 + (s - 5) // 2, True)
                                                 for s in (5, 7, 9, 11, 13, 15, 17)]


# --- Fields -----------------------------------------------------------------------------------------------------

def smoothstep(e0, e1, x):
    t = min(1.0, max(0.0, (x - e0) / (e1 - e0)))
    return t * t * (3 - 2 * t)


def smax(a, b, k_):
    h = max(k_ - abs(a - b), 0.0) / k_
    return max(a, b) + h * h * k_ * 0.25


def seg_dist(p, a, b):
    ax, ay = a
    bx, by = b
    dx, dy = bx - ax, by - ay
    t = max(0.0, min(1.0, ((p[0] - ax) * dx + (p[1] - ay) * dy) / (dx * dx + dy * dy)))
    return math.hypot(p[0] - ax - t * dx, p[1] - ay - t * dy)


def poly_dist(p, pts):
    return min(seg_dist(p, a, b) for a, b in zip(pts, pts[1:]))


def sunk(inside, depth, wall=0.3):
    """How far a recess lowers the surface: depth inside it, falling over `wall` at its edge."""
    return depth * smoothstep(0.0, wall, inside)


def rib_along(y, y0, y1):
    return smoothstep(y1 - 0.6, y1 + 0.6, y) * smoothstep(y0 + 0.6, y0 - 0.6, y)


def shoulder_z(ax, y):
    """The shoulders' top (|x| = ax): falling away outwards in a curve and a little down the screen, a roll along
    their top edge, the ribs down them."""
    u = min(1.0, max(0.0, (ax - 5.4) / 6.6))
    top, fall, power, down = SHOULDER
    z = top - fall * u ** power - down * (SHOULDER_TOP - y)
    below, w, h = SHOULDER_ROLL
    z += h * math.exp(-((SHOULDER_TOP - y - below) / w) ** 2) * (1.0 - 0.5 * u)
    for rx, y0, y1, h, w in (RIB2, RIB4):
        z += h * rib_along(y, y0, y1) * math.exp(-((ax + rx) / w) ** 2)
    return z


def body_base(x, y):
    """The organic body's top without its edge rounding: the lobes, the neck, the brow and the shoulders in a smooth
    union, low under the block; the ridges and the crease on the head, the visor and the pits."""
    ax = abs(x)
    (lx, ly), (rx, ry), lh = LOBE
    q = ((ax + lx) / rx) ** 2 + ((y - ly) / ry) ** 2       # (the lobes at x = +-3)
    lobe = EDGE_Z + (lh - EDGE_Z) * math.sqrt(max(0.0, 1.0 - q)) ** 0.8 if q < 1 else EDGE_Z
    y0, y1, hw, nh = NECK
    if y1 <= y <= y0:
        neck = EDGE_Z + (nh - EDGE_Z) * math.sqrt(max(0.0, 1.0 - min(1.0, (ax / hw) ** 2))) ** 0.7
    else:
        neck = EDGE_Z
    cy, hd, bh = BROW
    if abs(y - cy) < hd:
        brow = EDGE_Z + (bh - EDGE_Z) * math.sqrt(max(0.0, 1.0 - ((y - cy) / hd) ** 2)) ** 0.6
        brow -= (bh - EDGE_Z) * 0.6 * smoothstep(BROW_X[0], BROW_X[1], ax)
    else:
        brow = EDGE_Z
    under = UNDER_BLOCK if y < 0.5 and ax < 6.0 else EDGE_Z
    shoulders = shoulder_z(ax, y) if ax > 5.9 or y > 0.5 else EDGE_Z
    z = smax(smax(smax(lobe, neck, BLEND), brow, BLEND), under, 0.5)
    z = smax(z, shoulders, 0.7)
    horn = [(-hx, hy) for hx, hy in HORN]
    d = poly_dist((ax, y), horn)
    z += HORN_H * math.exp(-(d / HORN_W) ** 2)
    c0, cd, cw = CREASE
    z -= cd * math.exp(-(x / cw) ** 2) * smoothstep(c0, c0 + 1.4, y)
    (vx, vy), (vw, vh), vp, vd = VISOR
    v = (abs((x - vx) / vw) ** vp + abs((y - vy) / vh) ** vp) ** (1.0 / vp)
    z -= sunk((1.0 - v) * min(vw, vh), vd, 0.35)
    (ex, ey), er, edep = PITS
    z -= sunk(er - math.hypot(ax + ex, y - ey), edep, 0.25)
    return z


def in_visor(x, y):
    (vx, vy), (vw, vh), vp, _ = VISOR
    v = (abs((x - vx) / vw) ** vp + abs((y - vy) / vh) ** vp) ** (1.0 / vp)
    (ex, ey), er, _ = PITS
    return max((1.0 - v) * min(vw, vh), er - math.hypot(abs(x) + ex, y - ey))


def glint(x, y):
    (gx, gy), r = GLINT
    return r - math.hypot(abs(x) + gx, y - gy)


def crest(x, y):
    """Positive on the light crests: the ridges down the lobes and the neck, the shoulders' top rolls."""
    ax = abs(x)
    horn = [(-hx, hy) for hx, hy in HORN]
    best = CREST - poly_dist((ax, y), horn)
    if ax > CREASE_SIDE[1]:
        best = max(best, ROLL_CREST - abs(SHOULDER_TOP - y - SHOULDER_ROLL[0]))
    return best


def crease(x, y):
    """Positive in the dark creases: between the lobes and down the neck, where the shoulders meet the block."""
    ax = abs(x)
    best = 0.32 - ax if y > CREASE[0] + 0.5 else -1.0
    a, b = CREASE_SIDE
    if y < -0.3:
        best = max(best, min(ax - a, b - ax))
    return best


def shoulder_shade(x, y):
    """Positive on the shoulders below their top roll (the sprite shades them darker there), but for the ribs'
    crests."""
    ax = abs(x)
    if ax < CREASE_SIDE[1]:
        return -1.0
    below = SHOULDER_TOP - SHOULDER_ROLL[0] - ROLL_CREST - y
    for rx, y0, y1, _, _ in (RIB2, RIB4):
        if rib_along(y, y0, y1) > 0.5:
            below = min(below, abs(ax + rx) - CREST)
    return below


def block_top(x, y):
    top, slope = BLOCK_TOP
    return top + slope * y


# --- Materials --------------------------------------------------------------------------------------------------

def materials(lit):
    pal = k.level_palette()

    def purple(name, index, roughness=0.36):
        return k.material(name, palette=index, metallic=0.25, roughness=roughness)

    def glow(name, index, strength, roughness=0.25):
        return k.material(name, palette=index, metallic=0.0, roughness=roughness, emission=pal[index],
                          emission_strength=strength)
    m = {
        "outline": purple("pbeacon_outline", 0x51, 0.5),
        "deep": purple("pbeacon_deep", 0x53),
        "dark": purple("pbeacon_dark", 0x55),
        "mid": purple("pbeacon_mid", 0x57),
        "lit": purple("pbeacon_lit", 0x59, 0.32),
        "bright": purple("pbeacon_bright", 0x5b, 0.3),
    }
    if lit:
        m["slot"] = glow("pbeacon_slot_lit", 0xc7, 0.4)
        m["slot_hot"] = glow("pbeacon_slot_hot_lit", 0xcb, 0.5)
        m["tip"] = glow("pbeacon_tip_lit", 0x27, 0.3)
        m["strip"] = glow("pbeacon_strip_lit", 0xc6, 0.45)
        m["dots"] = [m["slot_hot"], m["slot"], m["tip"]]
        m["bar"] = glow("pbeacon_bar", 0xce, 0.6, 0.2)
    else:
        m["slot"] = glow("pbeacon_slot", 0xc4, 0.3)
        m["slot_hot"] = glow("pbeacon_slot_hot", 0xc8, 0.4)
        m["tip"] = glow("pbeacon_tip", 0x24, 0.2)
        m["strip"] = m["lit"]
        m["dots"] = [m["deep"]] * 3
    return m


# --- Parts ------------------------------------------------------------------------------------------------------

def body(m):
    """The organic body: one solid over the machine's plan (polish_ring_machine.relief()), its top body_base()
    rounded down to the outline, painted along smooth borders."""
    plan = ccw(chaikin(mirror_plan(PLAN_LEFT), 1))

    def height(x, y, d):
        rim = EDGE_RIM + (SHOULDER_RIM - EDGE_RIM) * smoothstep(7.0, 9.0, abs(x))
        return EDGE_Z + (body_base(x, y) - EDGE_Z) * round_edge(d, rim)

    def paint(x, y, d):
        if d < OUTLINE_D:
            return "outline"
        if glint(x, y) > 0:
            return "bright"
        if in_visor(x, y) > 0.05:
            return "outline"
        if crease(x, y) > 0:
            return "deep"
        if crest(x, y) > 0:
            return "lit"
        if shoulder_shade(x, y) > 0:
            return "dark"
        return "mid"

    borders = [(lambda x, y, d: d, OUTLINE_D), (lambda x, y, d: in_visor(x, y), 0.05),
               (lambda x, y, d: in_visor(x, y), 0.35), (lambda x, y, d: glint(x, y), 0.0),
               (lambda x, y, d: crease(x, y), 0.0), (lambda x, y, d: crest(x, y), 0.0),
               (lambda x, y, d: shoulder_shade(x, y), 0.0)]
    mats = {key: m[key] for key in ("outline", "deep", "dark", "mid", "lit", "bright")}
    return [relief("body", [plan], height, mats, paint=paint, side="outline", bottom=BOTTOM, spacing=0.58,
                   borders=borders, smooth_angle=50)]


def rect(x0, x1, y0, y1, r, segments=56):
    ring = mk.rounded_rect_ring(((x0 + x1) / 2, (y0 + y1) / 2), (x1 - x0) / 2, (y1 - y0) / 2, r, 0.0, segments)
    return [(p.x, p.y) for p in ring]


def block(m):
    """The block between the shoulders (columns 6-17 of rows 14-25), machined: its plan extruded up to its sloping
    top, its edges bevelled; the slots and the channel cut down its face (open at its foot), the ridges between them
    rounded bars; the slots' glowing floors and their brighter spots."""
    x0, x1, y0, y1, r_top, r_foot = BLOCK_PLAN
    # The plan: a rectangle, its upper corners rounded a little, its lower ones more.
    plan = []
    for (cx, cy), r, a0 in (((x1 - r_foot, y0 + r_foot), r_foot, -90), ((x1 - r_top, y1 - r_top), r_top, 0),
                            ((x0 + r_top, y1 - r_top), r_top, 90), ((x0 + r_foot, y0 + r_foot), r_foot, 180)):
        for i in range(9):
            a = math.radians(a0 + 90 * i / 8)
            plan.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    body_ = mk.wedge("block", plan, UNDER_BLOCK - 0.5, block_top, m["mid"])
    mk.bevel(body_, BLOCK_BEVEL, 3, 35)
    sx0, sx1, sy0, sy1, sr, sd = SLOT
    cutters = []
    for side in (-1, 1):
        outline = rect(sx0, sx1, sy0, sy1, sr) if side > 0 else [(-x, y) for x, y in reversed(rect(sx0, sx1, sy0, sy1, sr))]
        cutters.append(mk.wedge("slot_cut%d" % side, outline, 0.0, lambda x, y: block_top(x, y) + 3.0, m["deep"],
                                bottom=lambda x, y: block_top(x, y) - sd))
    cw, cy1, cd = CHANNEL
    cutters.append(mk.wedge("channel_cut", [(-cw, -13.5), (cw, -13.5), (cw, cy1), (-cw, cy1)], 0.0,
                            lambda x, y: block_top(x, y) + 3.0, m["deep"], bottom=lambda x, y: block_top(x, y) - cd))
    mk.boolean(body_, cutters, "DIFFERENCE")
    mk.cleanup(body_)
    mk.shade(body_, 35)

    def pick(c, n):
        top = block_top(c.x, c.y)
        if abs(c.x) < cw + 0.05 and c.z < top - 0.05:
            return m["deep"]                                    # the channel
        if sx0 - 0.05 < abs(c.x) < sx1 + 0.05 and c.z < top - 0.05 and c.y < sy1 + 0.05:
            return m["dark"]                                    # the slots' walls
        if n.z > 0.6 and c.y > BLOCK_EDGE:
            return m["lit"]                                     # the top edge
        if n.z < 0.6 and n.x < -0.5:
            return m["lit"]                                     # the left wall, in the light
        if n.z < 0.6 and (n.x > 0.5 or n.y < -0.5):
            return m["dark"]
        return None
    mk.paint(body_, pick)
    parts = [body_]
    # The ridges between the slots and the channel.
    mid, hw, h, ry0, ry1 = RIDGE
    for side in (-1, 1):
        rings = []
        n = 12
        for i in range(n + 1):
            y = ry0 + (ry1 - ry0) * i / n
            end = min(1.0, 0.45 + 0.55 * min(i, n - i) / 2.0)
            ring = []
            for j in range(10):
                a = 2 * math.pi * j / 10
                u, w = math.cos(a), math.sin(a)
                x = side * mid + hw * end * u
                ring.append(Vector((x, y, block_top(x, y) + (h * end * w if w > 0 else 0.3 * w))))
            rings.append(ring)
        ridge = k.loft("ridge%d" % side, rings, m["mid"])
        k.smooth(ridge, 60)
        mk.paint(ridge, lambda c, nn: m["lit"] if nn.x < -0.35 and nn.z > 0.2 else
                 m["dark"] if nn.x > 0.45 else None)
        parts.append(ridge)
    # The slots' floors: glowing plates in the cuts, dark green at their feet; the brighter spots.
    for side in (-1, 1):
        outline = rect(sx0 + 0.02, sx1 - 0.02, y0 + 0.05, sy1 - 0.02, sr - 0.02, 40)
        if side < 0:
            outline = [(-x, y) for x, y in reversed(outline)]
        plate = mk.wedge("floor%d" % side, outline, UNDER_BLOCK - 0.4,
                         lambda x, y: block_top(x, y) - sd + FLOOR_LIFT, m["slot"])
        bm = bmesh.new()
        bm.from_mesh(plate.data)
        bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-5, plane_co=(0, TIP_Y, 0),
                               plane_no=(0, 1, 0))
        bm.to_mesh(plate.data)
        bm.free()
        mk.paint(plate, lambda c, nn: m["tip"] if c.y < TIP_Y and nn.z > 0.5 else None)
        parts.append(plate)
        (hx, hy), (hrx, hry), hh = HOT
        z0 = block_top(side * hx, hy) - sd + FLOOR_LIFT - 0.02
        parts.append(mk.dome("hot%d" % side, (side * hx, hy), (hrx, hry, hh), z0, m["slot_hot"], 16, 3))
    return parts


def strips(m):
    """The rib down each shoulder's column 4 / 19 (rows 16-21): a rounded strip lying on the shoulder, its ends
    tapering, its underside sunk into it."""
    x0, y0, y1, hw, h = STRIP
    parts = []
    for side in (1, -1):
        rings = []
        n = 12
        for i in range(n + 1):
            y = y0 + (y1 - y0) * i / n
            taper = min(1.0, 0.35 + 0.65 * min(i, n - i) / 3)
            ring = []
            for j in range(10):
                a = 2 * math.pi * j / 10
                u, w = math.cos(a), math.sin(a)
                x = side * x0 + hw * taper * u
                z = body_base(x, y) + (h * taper * w if w > 0 else 0.3 * w)
                ring.append(Vector((x, y, z)))
            rings.append(ring)
        obj = k.loft("strip%d" % side, rings, m["strip"])
        k.smooth(obj, 60)
        parts.append(obj)
    return parts


def channel_floor(y):
    return block_top(0.0, y) - CHANNEL[2]


def dots(m):
    """The channel's three lights: small domes on its floor."""
    ys, r, h = DOTS
    return [mk.dome("dot%d" % i, (0.0, y), (r, r * 0.9, h), channel_floor(y) - 0.12, m["dots"][i], 14, 4)
            for i, y in enumerate(ys)]


def bar_z(x, y):
    """The surface the bar lies on: the block's top, the ridges, the slots' floors and the channel's."""
    ax = abs(x)
    top = block_top(x, y)
    sx0, sx1, *_ = SLOT
    if sx0 <= ax <= sx1:
        return top - SLOT[5] + FLOOR_LIFT
    if ax <= CHANNEL[0]:
        return channel_floor(y)
    mid, hw, h, _, _ = RIDGE
    if abs(ax - mid) < hw:
        return top + h * math.sqrt(max(0.0, 1.0 - ((ax - mid) / hw) ** 2))
    return top


def bar(m, row):
    """The bright bar across the block at a row: a ribbon a pixel wide lying on the block's face (over the ridges,
    down into the slots and the channel), from column 7 to column 16."""
    y = 13.5 - row
    n = 80
    xs = [-BAR_X + 2 * BAR_X * i / n for i in range(n + 1)]
    half = BAR_W / 2
    verts, faces = [], []
    for x in xs:
        z = max(bar_z(x, y - half), bar_z(x, y + half)) + BAR_LIFT
        verts += [(x, y - half, z), (x, y + half, z)]
    for i in range(n):
        faces.append((2 * i, 2 * i + 2, 2 * i + 3, 2 * i + 1))
    obj = k.mesh_object("bar", verts, faces, m["bar"])
    if obj.data.polygons[0].normal.z < 0:
        obj.data.flip_normals()
    k.smooth(obj, 80)
    return [obj]


# --- Build ------------------------------------------------------------------------------------------------------

def build():
    options = k.args()
    out = mk.outdir(options)
    only = options["only"].split(",") if "only" in options else None
    k.reset()
    dim, lit = materials(False), materials(True)
    strip_parts = strips(dim)
    dot_parts = dots(dim)
    base = body(dim) + block(dim) + strip_parts + dot_parts
    for obj in base:
        mk.apply(obj)
    triangulate(base)
    # The lit frames' colours: each dim material by name -> its lit counterpart.
    swap = {dim[key].name: lit[key] for key in ("slot", "slot_hot", "tip")}
    sheet = os.path.join(options["check"], "enemy_5.png") if "check" in options else None
    dim_materials = {obj.name: [mat.name for mat in obj.data.materials] for obj in base}
    for name, sprite, row, is_lit in FRAMES:
        if only and name not in only:
            continue
        for obj in base:
            for i, original in enumerate(dim_materials[obj.name]):
                dim_mat = bpy.data.materials[original]
                if not is_lit:
                    obj.data.materials[i] = dim_mat
                elif obj in strip_parts:
                    obj.data.materials[i] = lit["strip"]
                elif obj in dot_parts:
                    obj.data.materials[i] = lit["dots"][dot_parts.index(obj)]
                else:
                    obj.data.materials[i] = swap.get(dim_mat.name, dim_mat)
        extra = []
        if row is not None:
            extra = bar(lit, row)
            triangulate(extra)
        parts = base + extra
        bpy.context.view_layer.update()
        if "stats" in options:
            for obj in parts:
                print("    %-12s %6d" % (obj.name, mk.triangles([obj])))
        if sheet:
            mk.compare("%s (5 %d)" % (name, sprite), mk.coverage(parts, 24, 28), k.sprite_mask(sheet, sprite))
        bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
        mk.report(name, parts, os.path.join(out, name + ".glb"))
        if "preview" in options:
            mk.preview(options["preview"] + name, parts)
        for obj in extra:
            data = obj.data
            bpy.data.objects.remove(obj)
            bpy.data.meshes.remove(data)


if __name__ == "__main__":
    build()
