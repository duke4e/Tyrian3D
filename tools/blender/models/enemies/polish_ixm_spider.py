"""IXMUCANE's and SAWBLADES' big spider (sheet 8 sprites 229 beside 231, 2x2 each: one 48 x 28 picture; enemies 192 and
193 of episode 3, the top layer; their animation 229 229 233 233 233 273 273 273 233 233 233 229 and 231 235 275 the
same), polished (2026-10-22, round 34; it replaces wave3_y_boss.py's spider: spheres and lofted legs on wave3_y_kit's
pieced object, one frame).

How the levels place it (tools/content/tyrevents.py): event 7 (the top layer) puts 192 at x and 193 at x + 24 on the
same row, the sheet's layout: SAWBLADES t1010 (x 100) and t1020 (x 160), IXMUCANE t2010, t2020, t2710 and t2720 (the
same two places). Armour 20 each, worth nothing, no guns; they don't move (they scroll with the top layer). No other
enemy (launched ones included) shows 229 231 233 235 273 275, and no other sprite is their pixels mirrored, turned or
in other ramps; no episode-6 level takes these waves.

As the sprites and their 4x upscales draw it (columns and rows of the 48 x 28 picture; symmetric about column 23, the
right half the left one mirrored, darker: the light comes from the left): a red heart-shaped body (columns 20-26 of
rows 13-19: two glossy lobes of ramp 4, lit along their inner upper sides (0x4e beside the seam at row 15), a dark seam
down the middle, pointed at the bottom); over it a dark thorax (columns 21-25 of rows 8-12) with two grey ribs along it
(columns 22 and 24); on the thorax's top a red spike pointing up the screen (column 23 of rows 4-8, three wide at rows
6-7); under the heart two grey fangs (ramp 0) bowing out and curving in to their points at the bottom (columns 16-20
of rows 17-25 and their mirror image); and four tan legs a side (ramp 1), thick and smooth, their roots beside the
thorax and the heart: the first rising up the screen like a horn to its tip at row 1 (column 13), the second out to
the left and up to its tip at row 9 (column 9), the third along rows 18-19 to its knee at column 6 and up to row 12,
the fourth down beside the heart, along rows 23-24 to its knee at column 2 and up to row 19. The frames walk: 233 and
273 draw the first and third legs' tips one and two rows shorter, the second and fourth ones' one and two rows longer
(an alternating gait), and the fangs' lower halves one and two pixels further out (opening).

Built as a spider standing on its legs (the IXMUCANE crab's family, polish_tan_crab.py: its oval tubes broad across,
its tans cut into bands by the light a face gets), modelled in the picture's plane (x, y as the sprites draw them, z
up from the layer) and then sheared along the game camera's line of sight (y - z tan 20: polish_lava_grub.py's way),
so that the camera sees every part where the sprites draw it however high it stands:
- the legs: smooth oval tubes along curves through the sprite's legs (LEGS: control points, Chaikin-smoothed), rising
  from their roots at the body (z 3.4-3.8) to their knees (6.6-6.9) and down to their tips on the layer, tapering,
  broad across; fitted to the sprite's outline (MASKS: each frame's left half; Picture): each section moved across
  the leg onto its middle (the point farthest from the sprite's edge), its half-width that distance less OUTLINE_IN
  (nearly through the outline: its staircases' corners), capped where the legs meet the body or each other, smoothed
  along the leg, the tip carried on to the sprite's tip; a spur under the fourth leg, the second and third legs' roots
  (a tan coxa) and the thorax's tan flanks where the first legs spring from it; tans 0x12-0x1c by the light (the sun
  from the top left: the right legs come out darker, as the sprite draws them);
- the heart: two lobes lofted down the screen through elliptical sections (HEART: their bumps at the top, overlapping
  below them, meeting in the point), a dark seam along the crease where they meet; glossy reds 0x43-0x4e by the light,
  the glare along their inner upper sides, glowing a little in their own red (0.12-0.3: the slanted camera sees much of
  the side away from the sun);
- the thorax: a dark glossy loft (0x02) with two grey ribs along it, splayed at its front; the spike: a red bud on a
  narrow stalk, turned about an axis leaning up the screen, by the light, glowing a little;
- the fangs: grey oval tubes along the sprite's hooks (0x07-0x0c by the light), wider where they bow out.
The frame models (233 / 235 and 273 / 275) are the same spider with each leg's tip moved as its frame draws it (the last
control point the whole step, the two before it 0.6 and 0.25 of it), fitted to that frame's outline, and the fangs'
lower halves moved out; all keep the same origin (models.cfg: origin; the top layer).
Cut at x = 0 (the sprites' edge, half a pixel right of the axis) with polish_coral_manta.cut (caps in each part's
darkest colour, the faces' winding kept), each piece moved so that its sprite's middle is its origin, triangulated
(polish_k_pod.triangulate: the same output with and without --check) and joined (polish_deli_boss.join: a primitive
per material). No random numbers, no booleans.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up from the layer. The whole's origin is
the picture's middle (column 24, row 14): column c is x = c + 0.5 - 24, row r is y = 13.5 - r; the pieces' origins (their
sprites' middles) are (-12, 0) (229) and (12, 0) (231).

models.cfg: model ixm_spider_l / ixm_spider_r (unchanged) and the new ixm_spider_l_233, ixm_spider_r_235,
ixm_spider_l_273, ixm_spider_r_275 (enemies/<name>.glb origin); sprite 8 229 ixm_spider_l yaw=0, sprite 8 231
ixm_spider_r yaw=0 (unchanged); frame 8 233 ixm_spider_l_233, frame 8 235 ixm_spider_r_235, frame 8 273
ixm_spider_l_273, frame 8 275 ixm_spider_r_275.

Replaces wave3_y_boss.py (all of it: the spider was its only object; nothing imports it) and wave3_y_art.py's SPIDER.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (each frame's silhouette in the
camera's view against 229 beside 231 and the pieces against their sprites, also leaving the sprite's outline ring
out), --preview <prefix>, --whole <dir> (the uncut spider of each frame as a GLB), --only <name,...>.
"""
import math
import os
import sys

import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
import polish_machine_kit as mk  # noqa: E402
from polish_coral_manta import cut  # noqa: E402
from polish_deli_boss import join  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402
from polish_launched_flames import lit, vertex_normals  # noqa: E402
from polish_orb_red import band_split  # noqa: E402
from polish_sphere_nozzle import smoothstep  # noqa: E402
from polish_tan_crab import SUN, chaikin_open, oval_tube, resample  # noqa: E402

TAN_T = math.tan(math.radians(20.0))   # the game camera: 20 degrees off straight down, from the bottom of the screen
AXIS_X = -0.5                          # column 23: the spider's axis of symmetry


def P(c, r, z=0.0):
    """The picture's column c, row r (a pixel's middle at whole numbers), at height z."""
    return Vector((c + 0.5 - 24.0, 13.5 - r, z))


def CR(v):
    """The column and row of a point of the picture's plane (P's inverse)."""
    return v.x + 23.5, 13.5 - v.y


# --- The sprites' outline: the left halves (columns 0-23) of 229, 233 and 273; the right halves are their mirror images
# about column 23, pixel for pixel. The legs and the fangs are fitted to it (their middles and widths).

MASKS = {
    0: """
.............##.........
............###.........
............###.........
............###........#
............####......##
............#####.....##
.............#######.###
..............######.###
.........##....#########
........###....#########
........####...#########
.....##.################
....###..###############
....###...##############
....###....#############
....###.....############
....####......##########
....####################
.##..###################
###...##############.###
###....############...##
####........########....
.###################....
..##################....
..############...####...
...######.###.....####..
..........##.......####.
........................
""",
    1: """
........................
.............##.........
............###.........
............###........#
............####......##
............#####.....##
.............#######.###
.........##...######.###
........###....#########
........###....#########
........####...#########
........################
.....##..###############
....###...##############
....###....#############
....###.....############
....####......##########
.##.####################
###..###################
###...##############.###
###....############...##
####........#######.....
.##################.....
..#################.....
..############..####....
...######.###....####...
..........##......####..
........................
""",
    2: """
........................
........................
.............##.........
............###........#
............####......##
............#####.....##
.........##..#######.###
........###...######.###
........###....#########
........###....#########
........####...#########
........################
.........###############
.....##...##############
....###....#############
....###.....############
.##.####......##########
###.####################
###..###################
###...##############.###
###....############...##
####........######......
.#################......
..################......
..############.####.....
...######.###...####....
..........##.....####...
........................
""",
}


class Picture:
    """A frame's outline (48 x 28 pixels): how far a point lies inside it."""

    def __init__(self, frame):
        left = [[ch == "#" for ch in row] for row in MASKS[frame].strip("\n").splitlines()]
        self.opaque = [[left[r][c] if c < 24 else left[r][46 - c] for c in range(48)] for r in range(28)]

    def at(self, c, r):
        return 0 <= r < 28 and 0 <= c < 48 and self.opaque[r][c]

    def inside(self, c, r):
        """The distance from (column c, row r) to the nearest pixel outside the outline (0 outside)."""
        best = 6.0
        c0, r0 = int(round(c)), int(round(r))
        for rr in range(r0 - 6, r0 + 7):
            for cc in range(c0 - 6, c0 + 7):
                if self.at(cc, rr):
                    continue
                dx = max(abs(c - cc) - 0.5, 0.0)
                dy = max(abs(r - rr) - 0.5, 0.0)
                best = min(best, math.hypot(dx, dy))
        return best


# --- The parts (left side; the right side is their mirror image about AXIS_X) --------------------------------------

# The legs: control points (column, row, z) from the root at the body to the tip, the half-widths across along them
# ((fraction of the length, half-width); the other way FLAT of it), and how a frame step moves the tip (columns, rows):
# legs 1 and 3 shorter, 2 and 4 longer, a row a step (the second one's tip leaning out a little).
LEGS = [
    ("leg1", [(19.7, 12.9, 3.6), (18.5, 11.5, 5.4), (17.6, 9.6, 6.6), (16.7, 7.5, 6.9), (15.3, 5.9, 6.2),
              (14.1, 4.3, 4.6), (13.5, 2.7, 2.9), (13.4, 1.4, 1.5)],
     [(0.0, 2.2), (0.3, 2.2), (0.45, 3.0), (1.0, 3.0)], (0.0, 1.0)),
    ("leg2", [(19.8, 15.1, 3.8), (17.4, 14.0, 5.8), (14.5, 13.4, 6.8), (11.7, 12.7, 6.8), (10.2, 11.5, 5.6),
              (9.5, 10.1, 3.8), (9.3, 8.8, 2.0)],
     [(0.0, 2.1), (0.35, 2.1), (0.5, 3.0), (1.0, 3.0)], (-0.35, -1.0)),
    ("leg3", [(19.2, 18.3, 3.6), (16.6, 18.7, 5.6), (12.5, 18.8, 6.7), (8.7, 18.5, 6.8), (6.6, 17.5, 6.0),
              (5.6, 15.7, 4.4), (5.4, 13.7, 2.8), (5.45, 12.2, 1.5)],
     [(0.0, 1.9), (0.3, 1.9), (0.42, 3.0), (1.0, 3.0)], (0.0, 1.0)),
    ("leg4", [(15.0, 19.8, 3.4), (13.4, 21.1, 4.8), (12.2, 22.9, 6.0), (9.0, 23.6, 6.6), (5.6, 23.5, 6.6),
              (3.3, 22.8, 5.8), (2.0, 21.4, 4.0), (1.5, 19.3, 1.6)],
     [(0.0, 1.7), (0.22, 1.7), (0.32, 3.0), (1.0, 3.0)], (0.0, -1.0)),
]
FLAT = 0.74
SNAP, SNAP_STEPS = 1.2, 12      # how far across a limb's middle is looked for (pixels), in steps
OUTLINE_IN = 0.15               # a limb reaches nearly through the sprite's outline (its staircases: the corners)
TIP_REACH = 0.35                # its tip's last section that far from the sprite's edge (its cap reaches 0.3 beyond)
MIN_HW = 0.45
WIDTH_SMOOTH = 3                # the fitted widths averaged over this many sections either side
TIP_Z = 1.2                     # the tips' lowest middle (their sections reach down to about 0.4)
# The spur under the fourth leg (columns 10-11 of rows 24-25): from, to, radius.
SPUR = ((10.9, 23.8, 5.6), (11.1, 25.6, 3.4), 0.95)
# The fangs: control points (column, row, z) from the root under the heart's side to the point, their half-widths
# along them, and how far a frame step moves their lower part out (columns) between which rows.
FANG = ([(18.3, 16.5, 3.4), (17.6, 18.5, 3.0), (16.9, 20.2, 2.6), (16.7, 21.4, 2.2), (17.3, 22.4, 1.8), (18.2, 23.3, 1.45),
         (18.9, 24.2, 1.15), (19.7, 25.1, 0.85), (20.25, 25.65, 0.7)],
        [(0.0, 1.0), (0.3, 0.95), (0.42, 1.2), (0.52, 1.25), (0.64, 1.0), (0.8, 0.82), (0.92, 0.65), (1.0, 0.38)],
        (-1.0, 20.5, 24.5))
# The roots of the second and third legs, where they meet beside the heart (columns 14-18 of rows 15-17): (column, row,
# z) and radii.
COXA = ((16.4, 16.0, 4.2), (2.3, 1.5, 1.5))
# The thorax's tan flanks, where the first legs spring from it (columns 19-20 of rows 8-12).
FLANK = ((19.7, 10.2, 4.0), (1.45, 2.7, 1.5))
# The heart: one hull lofted down the screen through sections that are two lobes side by side (tyrkit.lobed_ring;
# y in the picture, each lobe's middle out from the axis, its half-width, its height above and below the hull's middle
# z), the two bumps at its top merging into its point; a dark seam along the crease where the lobes meet on top.
HEART = [(1.65, 1.75, 0.25, 0.3, 0.3, 3.7), (1.3, 1.75, 1.1, 1.35, 1.25, 3.7), (0.6, 1.75, 1.7, 2.15, 1.95, 3.7),
         (-0.5, 1.75, 2.1, 2.55, 2.2, 3.65), (-2.0, 1.7, 2.33, 2.7, 2.35, 3.6), (-3.5, 1.4, 2.2, 2.45, 2.15, 3.5),
         (-4.8, 0.95, 1.7, 2.0, 1.75, 3.3), (-5.8, 0.45, 1.0, 1.3, 1.15, 3.1), (-6.5, 0.1, 0.3, 0.4, 0.4, 3.0)]
SEAM_R = 0.3
GLARE = (22.3, 15.2, 1.2)                # the lobe's glare (column, row, radius in pixels)
# The thorax: sections (row, half-width, top z, bottom z) at the axis; its ribs (column, rows from, to, radius).
THORAX = [(13.4, 1.4, 4.0, 2.6), (12.7, 2.2, 4.8, 2.2), (11.0, 2.55, 5.1, 2.0), (9.4, 2.55, 5.05, 2.0),
          (8.3, 2.45, 4.85, 2.2), (7.6, 1.5, 4.5, 2.6)]
RIBS = (22.0, 8.2, 12.2, 0.42)
# The spike: from its stalk (column, row, z) to its tip, its radius along it.
SPIKE = ((23.0, 8.9, 4.6), (23.0, 2.75, 5.9), [(0.0, 0.8), (0.14, 1.3), (0.28, 2.2), (0.42, 2.3), (0.58, 1.75),
                                                (0.74, 1.3), (0.9, 0.85), (1.0, 0.04)])

# Colours (palette index; the light thresholds from polish_tan_crab.light's value).
TAN = ((0.2, 0.36, 0.52, 0.72), (0x12, 0x15, 0x17, 0x1a, 0x1c))
REDS = ((0.3, 0.52, 0.8, 0.98), (0x43, 0x46, 0x48, 0x4b, 0x4e))
RED_GLOW = {0x43: 0.12, 0x46: 0.16, 0x48: 0.2, 0x4b: 0.24, 0x4e: 0.3}
GREY = ((0.36, 0.6), (0x07, 0x0a, 0x0c))


def materials():
    m = {}
    for index in TAN[1]:
        m[index] = k.material(f"spider_tan_{index:x}", palette=index, metallic=0.05,
                              roughness=0.5 if index < 0x18 else 0.4)
    for index in REDS[1]:
        m[index] = lit(f"spider_red_{index:x}", index, RED_GLOW[index], roughness=0.24, metallic=0.2)
    for index in GREY[1]:
        m[index] = k.material(f"spider_grey_{index:x}", palette=index, metallic=0.45, roughness=0.3)
    m["dark"] = k.material("spider_dark", palette=0x02, metallic=0.35, roughness=0.32)
    return m


def light(n):
    """polish_tan_crab.light: how much light a face gets (facing up, and the sun)."""
    sun = max(0.0, n.dot(SUN))
    return 0.6 * n.z + 0.3 * sun + 0.1 * sun ** 6


def bands(levels, m):
    thresholds, indices = levels
    return [(-99.0, m[indices[0]])] + [(t, m[i]) for t, i in zip(thresholds, indices[1:])]


def interp(table, t):
    if t <= table[0][0]:
        return table[0][1]
    for (t0, v0), (t1, v1) in zip(table, table[1:]):
        if t <= t1:
            return v0 + (v1 - v0) * (t - t0) / (t1 - t0)
    return table[-1][1]


def moved_tip(points, step, frame):
    """The control points with the tip moved frame steps (the last point the whole way, the two before it 0.6 and 0.25
    of it: the lower leg longer or shorter, its bend kept)."""
    dc, dr = step
    out = [list(p) for p in points]
    for i, share in ((len(out) - 1, 1.0), (len(out) - 2, 0.6), (len(out) - 3, 0.25)):
        out[i][0] += dc * frame * share
        out[i][1] += dr * frame * share
    return [tuple(p) for p in out]


def fitted(path, picture):
    """The path's points moved across it onto the middle of the sprite's limb (the farthest from its edge, within
    SNAP pixels; the moves smoothed along it), its tip carried on along it to TIP_REACH from the edge."""
    n = len(path)
    moves = []
    for i, p in enumerate(path):
        a, b = path[max(i - 1, 0)], path[min(i + 1, n - 1)]
        t = Vector((b.x - a.x, b.y - a.y)).normalized()
        across = Vector((-t.y, t.x))
        best, best_s = -1.0, 0.0
        for j in range(-SNAP_STEPS, SNAP_STEPS + 1):
            s = SNAP * j / SNAP_STEPS
            c, r = CR(Vector((p.x + across.x * s, p.y + across.y * s, 0)))
            d = picture.inside(c, r)
            if d > best + 1e-6 or (abs(d - best) <= 1e-6 and abs(s) < abs(best_s)):
                best, best_s = d, s
        moves.append(across * best_s)
    smooth = []
    for i in range(n):
        near = [moves[j] for j in range(max(0, i - 2), min(n, i + 3))]
        smooth.append(sum(near, Vector((0, 0))) / len(near))
    out = [Vector((p.x + m.x, p.y + m.y, p.z)) for p, m in zip(path, smooth)]
    # The tip carried on in the picture's plane to the sprite's tip (its height kept, no lower than TIP_Z).
    tip, before = out[-1], out[-2]
    t = Vector((tip.x - before.x, tip.y - before.y, 0.0)).normalized()
    for _ in range(40):
        nxt = tip + t * 0.1
        if picture.inside(*CR(nxt)) < TIP_REACH:
            break
        tip = nxt
    tip.z = max(tip.z, TIP_Z)
    out[-1] = tip
    return out


def tube_along(name, ctrl, widths, mat, picture=None, per_point=2.5, around=12):
    """An oval tube (polish_tan_crab.oval_tube: broad across) along a smooth curve through the control points; with a
    picture, fitted to the sprite: on its limb's middle, its half-width the distance to the sprite's edge less a third
    of a pixel (two thirds into the outline), at most the widths table's (where limbs meet the body or each other);
    without, the widths table's."""
    path = resample(chaikin_open([tuple(P(c, r, z)) for c, r, z in ctrl], 3), 4 + int(per_point * len(ctrl)))
    if picture is not None:
        path = resample(fitted(path, picture), len(path))
    lengths = [0.0]
    for a, b in zip(path, path[1:]):
        lengths.append(lengths[-1] + (b - a).length)
    hws = []
    for p, s in zip(path, lengths):
        hw = interp(widths, s / lengths[-1])
        if picture is not None:
            hw = min(hw, max(MIN_HW, picture.inside(*CR(p)) - OUTLINE_IN))
        hws.append(hw)
    if picture is not None:   # (smoothed along the tube: the sprite's staircases are no bulges; the tip kept)
        n = len(hws)
        hws = [sum(hws[j] for j in range(max(0, i - WIDTH_SMOOTH), min(n, i + WIDTH_SMOOTH + 1))) /
               len(range(max(0, i - WIDTH_SMOOTH), min(n, i + WIDTH_SMOOTH + 1))) if i < n - 2 else hws[i]
               for i in range(n)]
    return oval_tube(name, path, [(hw, hw * FLAT) for hw in hws], mat, around=around)


def leg(m, name, ctrl, widths, step, frame, picture):
    return tube_along(name, moved_tip(ctrl, step, frame), widths, m[TAN[1][2]], picture)


def spur(m):
    a, b, r = SPUR
    pa, pb = P(*a), P(*b)
    axis = (pb - pa).normalized()
    side = axis.cross(Vector((0, 0, 1))).normalized()
    up = side.cross(axis).normalized()
    rings = []
    for t, rr in ((0.0, r), (0.45, r * 0.85), (0.8, r * 0.5), (1.0, 0.05)):
        p = pa.lerp(pb, t)
        rings.append([p + (side * math.cos(2 * math.pi * j / 10) + up * math.sin(2 * math.pi * j / 10)) * rr
                      for j in range(10)])
    obj = k.loft("spur", rings, m[TAN[1][2]], start_point=pa - axis * 0.3, end_point=pb + axis * 0.05)
    k.recalc_normals(obj)
    return obj


def fang(m, frame):
    ctrl, widths, (dc, r0, r1) = FANG
    moved = [(c + dc * frame * smoothstep(r0, r1, r), r, z) for c, r, z in ctrl]
    return tube_along("fang", moved, widths, m[GREY[1][1]], per_point=2.0, around=10)


def coxa(m):
    (c, r, z), radii = COXA
    return k.ellipsoid("coxa", tuple(P(c, r, z)), radii, m[TAN[1][2]], segments=16, rings_count=10)


def flank(m):
    (c, r, z), radii = FLANK
    return k.ellipsoid("flank", tuple(P(c, r, z)), radii, m[TAN[1][2]], segments=16, rings_count=10)


def heart_at(y):
    """The left lobe's section at y: its middle's offset from the axis, half-width, height above and below its middle z,
    and that z."""
    table = sorted(HEART)
    return tuple(interp([(row[0], row[j]) for row in table], y) for j in range(1, 6))


def lobe(m):
    """The heart's left lobe: lofted down the screen through elliptical sections (HEART), the lobes overlapping along
    the axis below their bumps (the crease where they meet is the seam)."""
    table = sorted(HEART)
    rings = []
    for i in range(1, 22):
        y = table[0][0] + (table[-1][0] - table[0][0]) * i / 22
        dx, hw, top, bottom, zc = heart_at(y)
        rings.append(k.ring(y, hw, 1.0, 24, z=zc, x=AXIS_X - dx, top=top, bottom=bottom, power=2.0))
    first, last = table[0], table[-1]
    return k.loft("lobe", rings, m[REDS[1][2]], start_point=(AXIS_X - first[1], first[0], first[5]),
                  end_point=(AXIS_X - last[1], last[0] + 0.08, last[5]))


def seam(m):
    """A dark line along the crease where the lobes meet on top, sunk into it."""
    pts = []
    table = sorted(HEART)
    for i in range(1, 28):
        y = table[0][0] + (table[-1][0] - table[0][0]) * i / 28
        dx, hw, top, bottom, zc = heart_at(y)
        q = 1.0 - (dx / hw) ** 2 if hw > dx else 0.0
        pts.append(Vector((AXIS_X, y, zc + top * math.sqrt(max(q, 0.0)) - 0.12)))
    rings = []
    for i, p in enumerate(pts):
        a, b = pts[max(i - 1, 0)], pts[min(i + 1, len(pts) - 1)]
        t = (b - a).normalized()
        side = Vector((1, 0, 0))
        up = side.cross(t).normalized()
        rings.append([p + (side * math.cos(2 * math.pi * j / 8) + up * math.sin(2 * math.pi * j / 8)) * SEAM_R
                      for j in range(8)])
    obj = k.loft("seam", rings, m["dark"])
    k.recalc_normals(obj)
    return obj


def thorax(m):
    rings = []
    for r, hw, top, bottom in reversed(THORAX):
        p = P(23.0, r)
        zc = (top + bottom) / 2
        rings.append(k.ring(p.y, hw, (top - bottom) / 2, 24, z=zc, x=AXIS_X, power=2.2))
    first, last = THORAX[-1], THORAX[0]
    obj = k.loft("thorax", rings, m["dark"], start_point=(AXIS_X, P(23, first[0] - 0.25).y, (first[2] + first[3]) / 2),
                 end_point=(AXIS_X, P(23, last[0] + 0.25).y, (last[2] + last[3]) / 2))
    return obj


def thorax_top(c, r):
    """The thorax's top at (column, row) (its sections interpolated; an ellipse across)."""
    rows = [(row, hw, top, bottom) for row, hw, top, bottom in THORAX]
    rows.sort()
    hw = interp([(row, w) for row, w, _, _ in rows], r)
    top = interp([(row, t) for row, _, t, _ in rows], r)
    bottom = interp([(row, b) for row, _, _, b in rows], r)
    u = abs(P(c, r).x - AXIS_X) / max(hw, 1e-3)
    if u >= 1:
        return (top + bottom) / 2
    return (top + bottom) / 2 + (top - bottom) / 2 * (1 - u ** 2.2) ** (1 / 2.2)


def rib(m):
    c, r0, r1, radius = RIBS
    pts = []
    for i in range(9):
        r = r0 + (r1 - r0) * i / 8
        cc = c - 0.45 * smoothstep(9.2, r0, r)       # (splayed out at the front, as the sprite's row 8)
        pts.append(P(cc, r, thorax_top(cc, r) - 0.12))
    rings = []
    for i, p in enumerate(pts):
        a, b = pts[max(i - 1, 0)], pts[min(i + 1, len(pts) - 1)]
        t = (b - a).normalized()
        side = t.cross(Vector((0, 0, 1))).normalized()
        up = side.cross(t).normalized()
        rr = radius * (0.7 + 0.3 * math.sin(math.pi * i / 8))
        rings.append([p + (side * math.cos(2 * math.pi * j / 10) + up * math.sin(2 * math.pi * j / 10)) * rr
                      for j in range(10)])
    obj = k.loft("rib", rings, m[GREY[1][1]], start_point=pts[0] + (pts[0] - pts[1]).normalized() * 0.3,
                 end_point=pts[-1] + (pts[-1] - pts[-2]).normalized() * 0.3)
    k.recalc_normals(obj)
    return obj


def spike(m):
    a, b, profile = SPIKE
    pa, pb = P(*a), P(*b)
    axis = (pb - pa).normalized()
    side = Vector((1, 0, 0))
    up = axis.cross(side).normalized()
    side = up.cross(axis).normalized()
    rings = []
    for i in range(1, 13):
        t = i / 13
        rr = interp(profile, t)
        p = pa.lerp(pb, t)
        rings.append([p + (side * math.cos(2 * math.pi * j / 14) + up * math.sin(2 * math.pi * j / 14)) * rr
                      for j in range(14)])
    obj = k.loft("spike", rings, m[REDS[1][2]], start_point=pa, end_point=pb)
    k.recalc_normals(obj)
    return obj


def mirrored(obj, name):
    copy = obj.copy()
    copy.data = obj.data.copy()
    copy.name = name
    bpy.context.scene.collection.objects.link(copy)
    copy.data.transform(Matrix.Translation((AXIS_X, 0, 0)) @ Matrix.Scale(-1, 4, (1, 0, 0)) @
                        Matrix.Translation((-AXIS_X, 0, 0)))
    copy.data.flip_normals()
    return copy


def shear(objects):
    """The picture's plane moved along the camera's line of sight (y - z tan 20)."""
    for obj in objects:
        for v in obj.data.vertices:
            v.co.y -= v.co.z * TAN_T
        obj.data.update()


# --- Painting (after the shear: by the faces the camera and the sun see) -----------------------------------------

def paint_light(obj, levels, m, extra=None):
    values = []
    for v, n in zip(obj.data.vertices, vertex_normals(obj)):
        value = light(n)
        if extra is not None:
            value += extra(v.co, n)
        values.append(value)
    band_split(obj, values, bands(levels, m))
    return obj


def glare():
    """The lobes' glare along their inner upper sides, where the sprite draws 0x4e (in the camera's view)."""
    c, r, radius = GLARE
    spots = [P(c, r).to_2d(), P(2 * 23.0 - c, r).to_2d()]

    def f(co, n):
        seen = Vector((co.x, co.y + co.z * TAN_T))
        d = min((seen - spot).length for spot in spots)
        return 0.45 * math.exp(-(d / radius) ** 2) * smoothstep(-0.2, 0.5, n.z)
    return f


# --- The model -----------------------------------------------------------------------------------------------------

def build_whole(frame):
    """The whole spider at a frame (0: 229 / 231, 1: 233 / 235, 2: 273 / 275), sheared and painted; [(object, the
    material its cuts are capped with)]."""
    m = materials()
    picture = Picture(frame)
    parts = []
    left = []
    for name, ctrl, widths, step in LEGS:
        left.append((leg(m, name, ctrl, widths, step, frame, picture), "tan"))
    left.append((spur(m), "tan"))
    left.append((coxa(m), "tan"))
    left.append((flank(m), "tan"))
    left.append((fang(m, frame), "grey"))
    left.append((lobe(m), "red"))
    left.append((rib(m), "grey"))
    for obj, kind in left:
        parts.append((obj, kind, -1))
        parts.append((mirrored(obj, obj.name + "_r"), kind, 1))
    parts.append((seam(m), "dark", 0))
    parts.append((thorax(m), "dark", 0))
    parts.append((spike(m), "red", 0))
    shear([p[0] for p in parts])
    out = []
    for obj, kind, side in parts:
        if kind == "tan":
            paint_light(obj, TAN, m)
        elif kind == "grey":
            paint_light(obj, GREY, m)
        elif kind == "red":
            paint_light(obj, REDS, m, glare() if obj.name.startswith("lobe") else None)
        k.smooth(obj, 60)
        cap = {"tan": m[TAN[1][0]], "grey": m[GREY[1][0]], "red": m[REDS[1][0]], "dark": m["dark"]}[kind]
        out.append((obj, cap))
    return out


PIECES = [("ixm_spider_l", 229, (-24.0, 0.0, -30.0, 30.0), (-12.0, 0.0)),
          ("ixm_spider_r", 231, (0.0, 24.0, -30.0, 30.0), (12.0, 0.0))]
FRAMES = [(0, {"ixm_spider_l": "ixm_spider_l", "ixm_spider_r": "ixm_spider_r"}, (229, 231)),
          (1, {"ixm_spider_l": "ixm_spider_l_233", "ixm_spider_r": "ixm_spider_r_235"}, (233, 235)),
          (2, {"ixm_spider_l": "ixm_spider_l_273", "ixm_spider_r": "ixm_spider_r_275"}, (273, 275))]


def outline_ring(mask):
    """The sprite's outline: its pixels next to a transparent one (they are its near-black 0x01)."""
    h, w = len(mask), len(mask[0])

    def empty(r, c):
        return not (0 <= r < h and 0 <= c < w) or not mask[r][c]
    return [[mask[r][c] and any(empty(r + dr, c + dc) for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)))
             for c in range(w)] for r in range(h)]


def compare_core(label, covered, mask):
    """The overlap leaving the sprite's outline ring out (neither counted for nor against)."""
    ring = outline_ring(mask)
    h, w = len(mask), len(mask[0])
    both = sum(covered[y][x] and mask[y][x] and not ring[y][x] for y in range(h) for x in range(w))
    either = sum((covered[y][x] or mask[y][x]) and not ring[y][x] for y in range(h) for x in range(w))
    print("silhouette overlap %s without the sprite's outline: %.3f" % (label, both / max(either, 1)))


def camera_view(objects):
    """Copies of objects moved back along the camera's line of sight (y + z tan 20): their top view is the camera's."""
    copies = []
    for obj in objects:
        copy = obj.copy()
        copy.data = obj.data.copy()
        bpy.context.scene.collection.objects.link(copy)
        for v in copy.data.vertices:
            v.co.y += v.co.z * TAN_T
        copies.append(copy)
    return copies


def remove(objects):
    for obj in objects:
        mesh = obj.data
        bpy.data.objects.remove(obj)
        bpy.data.meshes.remove(mesh)


def build():
    options = k.args()
    out = mk.outdir(options)
    only = set(options["only"].split(",")) if "only" in options else None
    for frame, names, sprites in FRAMES:
        if only is not None and not set(names.values()) & only:
            continue
        k.reset()
        whole = build_whole(frame)
        objects = [obj for obj, _ in whole]
        bpy.context.view_layer.update()
        if "check" in options:
            sheet = os.path.join(options["check"], "enemy_8.png")
            seen = camera_view(objects)
            bpy.context.view_layer.update()
            mask = k.sprite_mask(sheet, list(sprites))
            covered = mk.coverage(seen, 48, 28)
            mk.compare("whole, frame %d %d in the camera's view" % sprites, covered, mask)
            compare_core("whole, frame %d %d" % sprites, covered, mask)
            remove(seen)
        if "whole" in options:
            mk.report("ixm_spider_whole_%d" % sprites[0], objects,
                      os.path.join(options["whole"], "ixm_spider_whole_%d.glb" % sprites[0]))
        pieces = {}
        for piece, sprite, box, (ox, oy) in PIECES:
            name = names[piece]
            if only is not None and name not in only:
                continue
            made = []
            for obj, cap in whole:
                part = cut(obj, box, cap)
                if part is not None:
                    made.append(part)
            mk.transform(made, Matrix.Translation((-ox, -oy, 0.0)))
            triangulate(made)
            made = [join(made, name)]     # (one mesh: a primitive per material, not per part and material)
            pieces[name] = (made, sprites[0 if piece.endswith("_l") else 1])
        for obj, _ in whole:
            obj.hide_render = True
        for name, (made, sprite) in pieces.items():
            bpy.context.view_layer.update()
            if "check" in options:
                sheet = os.path.join(options["check"], "enemy_8.png")
                seen = camera_view(made)
                bpy.context.view_layer.update()
                covered, mask = mk.coverage(seen, 24, 28), k.sprite_mask(sheet, sprite)
                mk.compare("%s (8 %d) in the camera's view" % (name, sprite), covered, mask)
                compare_core("%s (8 %d)" % (name, sprite), covered, mask)
                remove(seen)
            bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
            mk.report(name, made, os.path.join(out, name + ".glb"))
            if "preview" in options:
                mk.preview(options["preview"] + name, made)


if __name__ == "__main__":
    build()
