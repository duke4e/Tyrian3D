"""The Sonic Wave's shots (shots sheet sprites 6 44 63 82 73 16 54 66 85 223 224 242 243 150 149 131 130 284 283 303
302 47 9 123 105 124 106 125 143 144, shots2 sprites 248 249 250 251: all 1x1, 12 x 14 cells), modelled (2026-10-30, the
third round of the energy shots' models; until then each was drawn as its sprite with volume and the automatic glow).
This script also holds the kit polish_shot_megaring.py builds its ring with (Wave: a band of the screen's plane between
two edges, round on top, on its bands' borders).

Who fires them (sprite numbers of the shots sheet; ports by their number in the shop's lists, power levels 1-11):
  The Sonic Wave rear (port 11, the first shop, 950), mode 1, a volley every 6 frames (sideways waves at 13 pixels a
  frame, living 100 frames; the others flying up or down the screen at 13):
    p1  6 44 (left, right)                    p7   105+124 (left), 106+125 (right), 224 223 (up-left, up-right)
    p2  6 44, 63 (up)                         p8   105+124, 106+125, 73 (up), 82 (down)
    p3  6 44, 224 223                         p9   105+124, 106+125, 73, 243 242 (down-left, down-right)
    p4  16 54 (left, right), 63               p10  105+124, 106+125, 73, 130 131 (down-left, down-right at 45)
    p5  16 54, 224 223                        p11  105+124, 106+125, 130 131, 149 150 (up-left, up-right at 45)
    p6  16 54 twice (4 above and below), 224 223
  105 above 124 (by -7 and +7: they meet) is one tall wave flying left, 106 above 125 its mirror image flying right
  (bx -2 and +2: they start overlapping and part at 26 pixels a frame). Mode 2 (every shot accelerating up the screen):
  73 at p1, 73 and 63 at p2-p5, from p6 the wide arch 143+144 (bx -6 and +6: its two halves meet) with 63 or 73 at
  its sides, two to four arches at p10-p11. The Sonic Impulse (front port 41, shop 4:21): 143+144 at every power (28
  pixels a frame up the screen), and at p4 and p11 the chevron shots2 248 249 250 251 (bx -18 -6 6 18: one 48-pixel
  chevron in four pieces). Enemies: weapon 76 (105 and 124 below it flying left at 5 pixels a frame, 106 and 125 right;
  ASTEROID2, AST. CITY, BONUS, New Deli, TORM, BOTANY A/B, ?TUNNEL?: enemies 550, 598, 600, 601, 772, 773). The
  MicroSol options 5 and 6 (specials 35, 36): 73. The second player (two-player games): the linked turret of rear
  ports 11, 28 and 33 picks its sprite by heading (shots.c linkSonicGr: 85 242 131 303 47 284 150 223 66 224 149 283 9
  302 130 243 for headings 0-15, heading k flying k x 22.5 degrees counter-clockwise from straight down), the charge
  cannon (rear port 11, weapons 464-468) 66, 73, 123, 143+144 and 73 by charge.

As the sprites draw them (ramp 12, the green: 0xc0 near black .. 0xcf light green): waves bright along their front
(the edge they fly towards) and darker behind, their ends trailing back:
- 66 an arch (a horseshoe) 12 wide and 13 tall, its brightest line (0xcc) a pixel inside its top, a gradient filling
  its top half (0xc9 .. 0xc0), its legs thinner and darker down to row 13; 85 the same upside down; 223 224 242 243,
  150 149 131 130, 284 283 303 302 and 47 9 the same arch drawn at the turret's other headings (the 45-degree ones as
  corners with straight arms).
- 63 a flatter arch (12 wide, rows 4-11), its top brightest (0xce); 82 the same upside down.
- 73 two arches one inside the other, the outer one's top white-green (0xcf), the inner one 0xcc; 16 and 54 the same
  lying on their sides (flying left and right), their legs trailing as thin lines.
- 6 a slim crescent standing on its end (14 tall, 4-5 wide), bright (0xce) a pixel inside its front; 44 its mirror.
- 105+124 (and 106+125): a fat crescent 23 tall, white-green (0xcf) over its front half, darker behind, its ends
  trailing back, five thin streaks trailing behind it.
- 143+144: the same wave lying on its back as a wide arch (23 wide, 13 tall), seven streaks hanging down from it.
- 123: a smaller arch with five streaks (12 x 14).
- shots2 248-251: a chevron 40 wide and 14 tall, a line 3 pixels wide, bright (0xcc-0xcf) down its middle.

The models, built with the pulse's method (polish_shot_pulse.py: half-bodies, round on top and flat underneath, since
the game's camera only ever sees shots from above; palette materials; an idealized heat in bands whose borders are the
mesh's own rings, so no face is cut; a raised hot core; at most 10 materials):
- Every wave is a Wave: a band lying on the ground between its outer edge (the front) and its inner edge (the back),
  both curves from one end through the apex to the other; across it its top rises steeply from the front to a crest
  near it and slopes down gently to the back (a shock front with its wake); its heat peaks at the crest and falls
  towards the back much more than towards the front, and falls along it from the apex to the ends. The mesh's rows run
  along the wave on the bands' borders (each border two rows, in front of the crest and behind it), so the colours lie
  in stripes along it, a bright crest and a darker wake; the borders ripple a little. Along the crest a core of white
  green (0xcf) stands out of the top: the bright line of the sprites.
- shot_sonic (66, and turned onto its fifteen other headings with yaw= and at=), shot_sonic_2 (63, 82), shot_sonic_3
  (73, 16, 54: two waves one inside the other), shot_sonic_4 (6, 44: the slim crescent), all authored apex up;
  shot_sonic_123 (123): a low dark dome with five bright ribs running down it (the sprite's stripes).
- The big waves: one fat wave with streaks trailing behind (thin lofts whose roots lie inside the wave's back), built
  whole and cut into the sprites the game moves together (polish_machine_kit.cut), each piece moved so that its
  sprite's centre is its origin: 105 and 124 (the wave flying left, cut across its middle), 106 and 125 (its mirror
  image), 143 and 144 (the wide arch, cut down its middle), and the chevron shots2 248-251 (a Wave with an angular
  apex and straight arms, cut in four). The pieces' model lines take "origin" and their shot lines height= half the
  whole's height down, so that each whole is centred on the player's layer like the other shots.

Six materials a model (five bands of the green, 0xc2 0xc5 0xc8 0xca 0xcc, glowing 0.2-0.56, and the core's 0xcf at
0.62); 424-1 322 triangles.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera; a 1x1 model's
origin at its sprite's centre (pixel 6, 7 of the cell: column c is x = c + 0.5 - 6, row r is y = 6.5 - r); the big
waves built round their sprites' shared edge or corner; built on z = 0.

models.cfg: see the block's comment; --check prints every line's silhouette against its sprite and the at= that lays
each turned model on its sprite (the yaw kept at the heading's).

Run: Blender -b --factory-startup -P tools/blender/models/shots/polish_shot_sonic.py -- [--only <name,...>]
     [--outdir <dir>] (default assets/models/shots) [--check <sheets dir>] (silhouettes against <dir>/shots.png and
     shots2.png, from TYR3D_EXTRACT) [--preview <prefix>] (top, three-quarter and game-camera views)
"""
import math
import os
import sys

import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polish_shot_fireball as kit  # noqa: E402
from polish_shot_fireball import k, mk, triangulate, view, crossings, ring_sequence, clean, materials, curve  # noqa
from polish_shot_pulse import mesh_from_rings  # noqa: E402

OUTDIR = kit.OUTDIR
FIRE_ROUGHNESS, CORE_ROUGHNESS = kit.FIRE_ROUGHNESS, kit.CORE_ROUGHNESS


# === The kit: paths and the Wave ======================================================================================

def chaikin_open(points, iterations=2):
    """Rounds an open polyline's corners, keeping its ends."""
    return mk.chaikin(points, iterations=iterations, closed=False)


def resample(points, count, closed=False):
    """count points evenly spaced along a polyline (closed: round the loop, the first not repeated), with the fraction
    of the length at each."""
    pts = [tuple(p) for p in points] + ([tuple(points[0])] if closed else [])
    lengths = [0.0]
    for a, b in zip(pts, pts[1:]):
        lengths.append(lengths[-1] + math.hypot(b[0] - a[0], b[1] - a[1]))
    total = lengths[-1]
    out, fractions = [], []
    n = count if closed else count - 1
    for i in range(count):
        target = total * i / n
        j = max(0, min(len(pts) - 2, next((k_ for k_ in range(len(lengths) - 1) if lengths[k_ + 1] >= target),
                                          len(pts) - 2)))
        seg = lengths[j + 1] - lengths[j]
        f = (target - lengths[j]) / seg if seg > 1e-12 else 0.0
        a, b = pts[j], pts[j + 1]
        out.append((a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f))
        fractions.append(i / n)
    return out, fractions


def arch_path(right_half, count, smooth=2):
    """A symmetric path from its left end through the apex to its right end, from its right half (apex first, x >= 0),
    rounded and resampled: (points, u) with u from -1 (the left end) through 0 (the apex) to 1 (the right end)."""
    full = [(-x, y) for x, y in reversed(right_half[1:])] + [tuple(p) for p in right_half]
    full = chaikin_open(full, smooth)
    points, fractions = resample(full, count)
    return points, [2.0 * f - 1.0 for f in fractions]


def profile(s, crest, back):
    """The height across a wave (0 at the front edge and at the back edge, 1 at the crest): a quarter ellipse up the
    front, (1 - t^2)^back down the back (0.5 round, over 1 a soft toe)."""
    if s <= crest:
        return math.sqrt(max(0.0, 1.0 - ((crest - s) / crest) ** 2))
    t = min((s - crest) / (1.0 - crest), 1.0)
    return max(0.0, 1.0 - t * t) ** back


class Wave:
    """A wave lying on the ground: a band between its outer edge (the front, s = 0) and its inner edge (the back,
    s = 1), outer and inner the same count of points from one end to the other (or round a loop: closed), u the
    position of each along it (open waves: -1 .. 1, 0 the apex); height(u) its crest's height; heat(s, u) rising across
    to its peak and falling to the back at every u; bands [(lowest heat, palette index, emission)] ascending. Its rows
    are the bands' borders (each band border two rows, in front of the peak and behind it, waving a little: waves =
    (how many along it, how far (s), how much each border's are turned against the one before)), with rows between them
    where they lie further apart than gap, so that every face lies in one band; a flat underside in the darkest band;
    open ends where the edges don't meet closed with a cap."""

    def __init__(self, outer, inner, us, height, heat, bands, crest=0.3, back=1.0, closed=False, waves=(3.0, 0.02, 1.9),
                 gap=0.2, head=(0.5,), tail=(0.5,)):
        self.outer, self.inner, self.us = outer, inner, us
        self.height, self.heat, self.bands = height, heat, bands
        self.crest, self.back, self.closed = crest, back, closed
        self.waves, self.gap, self.head, self.tail = waves, gap, head, tail

    def point(self, s, j):
        (ox, oy), (ix, iy) = self.outer[j], self.inner[j]
        return Vector((ox + (ix - ox) * s, oy + (iy - oy) * s,
                       self.height(self.us[j]) * profile(s, self.crest, self.back)))

    def at(self, s, jf):
        """point() between samples (jf a fractional sample index)."""
        j = min(max(int(math.floor(jf)), 0), len(self.us) - 2)
        f = jf - j
        return self.point(s, j).lerp(self.point(s, j + 1), f)

    def curves(self):
        thresholds = [b[0] for b in self.bands[1:]]
        n = len(self.us)
        rise = [[0.0] * n for _ in thresholds]
        fall = [[1.0] * n for _ in thresholds]
        for j, u in enumerate(self.us):
            for i, v in enumerate(thresholds):
                rise[i][j], fall[i][j] = crossings(lambda s, u=u: self.heat(s, u), v)
        many, reach, turn_ = self.waves
        for i in range(len(thresholds)):
            for j, u in enumerate(self.us):
                closed_ = fall[i][j] - rise[i][j] < 1e-6
                wave = reach * math.sin(many * math.pi * u + turn_ * i)
                if rise[i][j] > 1e-6:
                    rise[i][j] = min(max(rise[i][j] + wave, 0.01), 0.99)
                if fall[i][j] < 1 - 1e-6:
                    fall[i][j] = min(max(fall[i][j] + wave, 0.01), 0.99)
                if closed_:
                    fall[i][j] = rise[i][j] = (rise[i][j] if rise[i][j] > 1e-6 else fall[i][j])
        borders = [list(r) for r in rise] + [list(f) for f in reversed(fall)]
        labels = list(range(1, len(thresholds) + 1)) + list(range(len(thresholds) - 1, -1, -1))
        for i in range(1, len(borders)):
            borders[i] = [max(b, p) for b, p in zip(borders[i], borders[i - 1])]
        return ring_sequence(borders, labels, 0, self.gap, None, self.head, self.tail)

    def build(self, name, mats):
        curves, front_band, back_band = self.curves()
        n = len(self.us)
        rows = [[0.0] * n] + [c for c, _ in curves] + [[1.0] * n]
        row_bands = [front_band] + [band for _, band in curves[:-1]] + [back_band]
        verts = []
        for ss in rows:
            verts += [self.point(s, j) for j, s in enumerate(ss)]
        faces, fmats = [], []
        spans = range(n) if self.closed else range(n - 1)
        for r in range(len(rows) - 1):
            a, b = r * n, (r + 1) * n
            for j in spans:
                jj = (j + 1) % n
                faces.append((a + j, a + jj, b + jj, b + j))
                fmats.append(row_bands[r])
        last = (len(rows) - 1) * n
        for j in spans:  # (the flat underside, never seen: the darkest band)
            jj = (j + 1) % n
            faces.append((j, last + j, last + jj, jj))
            fmats.append(0)
        if not self.closed:
            for j in (0, n - 1):  # (open ends: a cap through the section)
                (ox, oy), (ix, iy) = self.outer[j], self.inner[j]
                if math.hypot(ix - ox, iy - oy) > 1e-3:
                    faces.append(tuple(r * n + j for r in range(len(rows))))
                    fmats.append(0)
        obj = k.mesh_object(name, verts, faces)
        for m in mats:
            obj.data.materials.append(m)
        for poly, m in zip(obj.data.polygons, fmats):
            poly.material_index = m
        clean(obj)
        k.recalc_normals(obj)
        return k.smooth(obj, 70)


def crest_core(name, wave, s_line, j0, j1, width, lift, bands, mats, rings=18, segments=5):
    """A core of plasma standing out of a wave's top along a line across it at s_line, from sample j0 to j1
    (fractional): pointed at both ends and full in its middle, width its half-width, lift how far it stands out of the
    wave's top; bands [(from d, palette index, emission)] by d, the distance from its middle (0) to its ends (1)."""
    angles = [math.pi * a / segments for a in range(segments + 1)]
    out, ds = [], []
    for i in range(1, rings):
        t = i / rings
        jf = j0 + (j1 - j0) * t
        f = math.sin(math.pi * t) ** 0.6
        c = wave.at(s_line, jf)
        o, n_ = wave.at(0.0, jf), wave.at(1.0, jf)
        across = Vector((n_.x - o.x, n_.y - o.y, 0.0))
        across = across.normalized() if across.length > 1e-9 else Vector((1.0, 0.0, 0.0))
        w = max(width * f, 0.03)
        h = c.z + lift * f
        out.append([Vector((c.x + across.x * w * math.cos(a), c.y + across.y * w * math.cos(a), h * math.sin(a)))
                    for a in angles])
        ds.append(abs(2 * t - 1))
    tips = (wave.at(s_line, j0), wave.at(s_line, j1))
    tips = [Vector((p.x, p.y, 0.0)) for p in tips]

    def band_at(d):
        return max(i for i, b in enumerate(bands) if d >= b[0] - 1e-9)
    faces = [band_at((a + b) / 2) for a, b in zip(ds[:-1], ds[1:])] + [len(bands) - 1, len(bands) - 1]
    obj = mesh_from_rings(name, out, faces, tips, mats, len(bands) - 1)
    clean(obj)
    k.recalc_normals(obj)
    return k.smooth(obj, 80)


def heat_field(along, front_drop, back_drop, peak, back_power=0.8):
    """A wave's heat: along(|u|) at its peak across (peak: s), falling to along * (1 - front_drop) at its front edge
    (as the square of the way) and to along * (1 - back_drop) at its back (to the power back_power: under 1 falling
    fast behind the peak, over 1 a broad plateau)."""
    a = curve(along)

    def heat(s, u):
        h = a(min(abs(u), 1.0))
        if s < peak:
            return h * (1.0 - front_drop * ((peak - s) / peak) ** 2)
        return h * (1.0 - back_drop * ((s - peak) / (1.0 - peak)) ** back_power)
    return heat


def height_curve(points):
    c = curve(points)
    return lambda u: max(c(min(abs(u), 1.0)), 0.0)


# The bands of ramp 12 (the green), two or three shades apart: (lowest heat, palette index, emission); the cores'
# (from d, index, emission): white-green (0xcf). Six materials a model (each material is one more draw of the model in
# every pass: eight cost about 0.5 ms in the busiest scene, see the report).
BANDS = [(-99.0, 0xc2, 0.2), (4.0, 0xc5, 0.3), (7.0, 0xc8, 0.4), (9.4, 0xca, 0.48), (11.3, 0xcc, 0.56)]
CORE_BANDS = ((0.0, 0xcf, 0.62),)


def wave_mats(prefix):
    return materials(prefix, BANDS)


def core_mats(prefix):
    return materials(prefix + "_core", CORE_BANDS, CORE_ROUGHNESS)


# === The 1x1 waves ====================================================================================================
# Each: its outer and inner edges' right halves (apex first; x >= 0; both ending at the same tip), the samples along
# it, the crest's height along it (|u|: 0 the apex, 1 the end), where the crest lies across (s) and how the back falls,
# the heat (along |u|; how much it falls to the front edge and to the back edge, and how; where it peaks across), the
# core (from |u| = -c to c, its half-width, lift).

ARCHES = {
    # 66: a horseshoe, its top filled, its legs trailing down to row 13
    "arch": dict(
        outer=[(0.0, 6.05), (1.5, 5.85), (2.75, 5.15), (3.75, 4.1), (4.5, 3.0), (5.0, 1.9), (5.45, 0.6), (5.75, -0.8),
               (5.95, -2.4), (5.95, -4.2), (5.75, -5.7), (5.2, -6.75)],
        inner=[(0.0, -0.75), (1.0, -0.95), (1.75, -1.6), (2.3, -2.5), (2.75, -3.6), (3.15, -4.7), (3.65, -5.8),
               (4.4, -6.6), (5.2, -6.75)],
        samples=29, height=((0.0, 2.1), (0.3, 1.9), (0.55, 1.45), (0.8, 0.95), (0.93, 0.55), (1.0, 0.0)),
        crest=0.22, back=1.3,
        along=((0.0, 12.8), (0.22, 12.4), (0.4, 11.0), (0.52, 9.9), (0.63, 8.7), (0.74, 7.4), (0.84, 5.6),
               (0.92, 3.6), (1.0, 1.2)),
        front=0.5, back_drop=0.9, peak=0.2, back_power=0.75,
        core=(0.58, 0.8, 0.46),
    ),
    # 63: a flatter arch, its top brightest
    "flat": dict(
        outer=[(0.0, 3.05), (1.6, 2.92), (3.0, 2.45), (4.2, 1.75), (5.2, 0.9), (5.85, -0.1), (6.0, -1.3),
               (5.95, -2.8), (5.75, -4.1), (5.45, -5.0)],
        inner=[(0.0, -1.35), (1.7, -1.55), (2.7, -2.0), (3.5, -2.7), (4.3, -3.55), (4.95, -4.4), (5.45, -5.0)],
        samples=27, height=((0.0, 1.65), (0.35, 1.5), (0.6, 1.1), (0.85, 0.6), (1.0, 0.0)),
        crest=0.3, back=1.2,
        along=((0.0, 13.8), (0.2, 13.2), (0.36, 11.8), (0.5, 9.6), (0.62, 8.2), (0.75, 5.6), (0.88, 3.2),
               (1.0, 1.0)),
        front=0.5, back_drop=0.9, peak=0.3, back_power=0.75,
        core=(0.5, 0.75, 0.42),
    ),
    # 73: the outer of two arches (its top white-green), and the inner one
    "double_outer": dict(
        outer=[(0.0, 6.05), (1.5, 5.75), (2.65, 5.05), (3.55, 4.05), (4.1, 3.0), (4.5, 1.9), (4.8, 0.7),
               (4.95, -0.8), (5.0, -2.6), (4.95, -4.5), (4.8, -6.0), (4.45, -6.95)],
        inner=[(0.0, 1.75), (1.25, 1.55), (2.15, 0.95), (2.85, 0.0), (3.35, -1.2), (3.7, -2.6), (3.9, -4.1),
               (4.15, -5.6), (4.45, -6.95)],
        samples=29, height=((0.0, 1.85), (0.3, 1.7), (0.5, 1.3), (0.75, 0.8), (0.92, 0.5), (1.0, 0.0)),
        crest=0.45, back=0.9,
        along=((0.0, 15.0), (0.18, 14.2), (0.32, 12.2), (0.42, 10.4), (0.52, 9.0), (0.62, 6.6), (0.72, 5.6),
               (0.84, 5.2), (0.93, 3.6), (1.0, 1.4)),
        front=0.6, back_drop=0.8, peak=0.47, back_power=0.8,
        core=(0.42, 0.75, 0.42),
    ),
    "double_inner": dict(
        outer=[(0.0, 1.0), (1.15, 0.82), (2.0, 0.2), (2.65, -0.8), (3.05, -2.0), (3.15, -3.0), (3.05, -3.95)],
        inner=[(0.0, -1.55), (0.85, -1.5), (1.45, -1.95), (1.95, -2.65), (2.45, -3.35), (3.05, -3.95)],
        samples=19, height=((0.0, 1.3), (0.4, 1.15), (0.75, 0.7), (1.0, 0.0)),
        crest=0.3, back=1.0,
        along=((0.0, 12.6), (0.25, 11.6), (0.45, 9.8), (0.65, 6.6), (0.85, 3.8), (1.0, 1.4)),
        front=0.5, back_drop=0.9, peak=0.3, back_power=0.75,
        core=None,
    ),
    # 6 stood up (apex up; its lines turn it onto its side): a slim crescent bright a pixel inside its front, its ends
    # bending back past the cell's edges
    "slim": dict(
        outer=[(0.0, 4.05), (2.0, 3.9), (3.6, 3.35), (4.9, 2.55), (5.9, 1.55), (6.6, 0.4), (7.0, -0.9), (7.15, -2.2),
               (7.05, -3.3)],
        inner=[(0.0, -0.95), (1.6, -1.05), (2.8, -1.45), (3.9, -2.0), (4.9, -2.5), (5.8, -2.95), (6.5, -3.3),
               (7.05, -3.3)],
        samples=27, height=((0.0, 1.55), (0.5, 1.4), (0.8, 1.0), (0.94, 0.6), (1.0, 0.0)),
        crest=0.28, back=1.1,
        along=((0.0, 14.0), (0.15, 13.2), (0.33, 12.0), (0.5, 10.2), (0.65, 9.0), (0.8, 7.6), (0.93, 5.4),
               (1.0, 3.0)),
        front=0.55, back_drop=0.9, peak=0.26, back_power=0.7,
        core=(0.64, 0.7, 0.42),
    ),
}


def build_arch(name, spec, prefix, mats, cmats, shift=(0.0, 0.0)):
    outer, u = arch_path(spec["outer"], spec["samples"])
    inner, _ = arch_path(spec["inner"], spec["samples"])
    sx, sy = shift
    outer = [(x + sx, y + sy) for x, y in outer]
    inner = [(x + sx, y + sy) for x, y in inner]
    wave = Wave(outer, inner, u, height_curve(spec["height"]),
                heat_field(spec["along"], spec["front"], spec["back_drop"], spec["peak"], spec["back_power"]), BANDS,
                crest=spec["crest"], back=spec["back"], gap=0.3)
    parts = [wave.build(name + "_wave", mats)]
    if spec.get("core") is not None:
        c, w, lift = spec["core"]
        n = len(u) - 1
        j0, j1 = n * (1 - c) / 2, n * (1 + c) / 2
        parts.append(crest_core(name + "_core", wave, spec["peak"], j0, j1, w, lift, CORE_BANDS, cmats))
    return parts


# === The big waves: a fat wave with streaks trailing behind ===========================================================
# Built apex up round the cap's axis (x = 0), the cap's outer apex at y = top: the cap's outer edge a circle of radius
# R (its middle R below the apex) out to the ends at +-span degrees from the apex (past about 75 degrees the circle
# bends back behind the wave: the ends trail); its inner edge where the circle's radius meets the back line (y0 -
# bow x^2: the sprites' fat waves are flat behind), but at least depth(|u|) inside the outer edge near the ends;
# streaks at x (their roots inside the cap's back, their tips at y), their half-width.

BIG = {
    "side": dict(  # 105+124 stood up (apex up; turned to fly left after it is built)
        top=6.0, radius=11.6, span=86.0, back_line=(-2.2, 0.02),
        depth=((0.0, 1.5), (0.75, 1.6), (0.92, 1.2), (1.0, 0.0)),
        samples=39, height=((0.0, 2.9), (0.4, 2.6), (0.7, 1.8), (0.9, 0.9), (1.0, 0.0)),
        crest=0.2, back=1.4,
        along=((0.0, 14.6), (0.3, 14.2), (0.55, 12.8), (0.72, 11.0), (0.85, 8.8), (0.94, 6.4), (1.0, 3.8)),
        front=0.42, back_drop=0.5, peak=0.22, back_power=1.6,
        core=(0.72, 1.0, 0.5),
        streaks=[(-8.0, -6.0), (-4.0, -6.0), (0.0, -6.0), (4.0, -6.0), (8.0, -6.0)], streak_width=0.5,
    ),
    "up": dict(  # 143+144: the wide arch
        top=7.0, radius=12.0, span=80.0, back_line=(-0.6, 0.008),
        depth=((0.0, 1.4), (0.75, 1.5), (0.92, 1.1), (1.0, 0.0)),
        samples=39, height=((0.0, 2.8), (0.4, 2.5), (0.7, 1.7), (0.9, 0.85), (1.0, 0.0)),
        crest=0.2, back=1.4,
        along=((0.0, 14.6), (0.3, 14.2), (0.55, 12.8), (0.72, 11.0), (0.85, 8.8), (0.94, 6.4), (1.0, 3.8)),
        front=0.42, back_drop=0.5, peak=0.22, back_power=1.6,
        core=(0.72, 1.0, 0.5),
        streaks=[(-11.0, -6.0), (-8.0, -6.0), (-4.0, -5.0), (0.0, -4.0), (4.0, -5.0), (8.0, -6.0), (11.0, -6.0)],
        streak_width=0.5,
    ),
}
# The streaks: dim green lines (their heat along them from the root to the tip, cooler at their sides), as wide along
# most of their length, rounding off at their tips.
STREAK_ALONG = ((0.0, 8.6), (0.35, 7.6), (0.7, 5.6), (1.0, 3.0))
STREAK_ACROSS = ((0.0, 1.4), (1.0, 1.4))


def streak_width(w):
    return curve(((0.0, 0.0), (0.04, w * 0.75), (0.12, w), (0.7, w * 0.92), (0.88, w * 0.72), (0.97, w * 0.35),
                  (1.0, 0.0)))


def big_edges(spec):
    """The cap's outer edge (a circle of the spec's radius, its top at y = top, from -span to span degrees round from
    the apex) and its inner edge (along the circle's radius to the back line, at least depth(|u|) in), from the left end
    through the apex to the right end, and u along them."""
    top, r, span = spec["top"], spec["radius"], math.radians(spec["span"])
    y0, bow = spec["back_line"]
    cy = top - r
    depth = curve(spec["depth"])
    n = spec["samples"]
    outer, inner, us = [], [], []
    for i in range(n):
        u = 2.0 * i / (n - 1) - 1.0
        a = u * span
        nx, ny = math.sin(a), math.cos(a)
        x, y = r * nx, cy + r * ny
        # (inwards along the radius until y reaches the back line: y - d ny = y0 - bow (x - d nx)^2, solved by steps)
        d = 0.0
        if ny > 0.05:
            lo, hi = 0.0, r
            for _ in range(40):
                mid = (lo + hi) / 2
                if y - mid * ny > y0 - bow * (x - mid * nx) ** 2:
                    lo = mid
                else:
                    hi = mid
            d = lo
        dmin = depth(min(abs(u), 1.0))
        d = max(d, dmin) if abs(u) < 0.999 else 0.0
        outer.append((x, y))
        inner.append((x - nx * d, y - ny * d))
        us.append(u)
    return outer, inner, us


def build_big(name, spec, prefix):
    mats, cmats = wave_mats(prefix), core_mats(prefix)
    outer, inner, us = big_edges(spec)
    wave = Wave(outer, inner, us, height_curve(spec["height"]),
                heat_field(spec["along"], spec["front"], spec["back_drop"], spec["peak"], spec["back_power"]), BANDS,
                crest=spec["crest"], back=spec["back"], gap=0.22)
    parts = [wave.build(name + "_wave", mats)]
    c, w, lift = spec["core"]
    n = len(us) - 1
    parts.append(crest_core(name + "_core", wave, spec["peak"], n * (1 - c) / 2, n * (1 + c) / 2, w, lift, CORE_BANDS,
                            cmats, rings=28))
    # The streaks: their roots 2 pixels inside the cap's back where they leave it (buried in its back slope).
    y0, bow = spec["back_line"]
    for i, (x, tip) in enumerate(spec["streaks"]):
        root = y0 - bow * x * x + 2.0
        loft = kit.Loft(x, root, tip, streak_width(spec["streak_width"]),
                        kit.loft_heat(STREAK_ALONG, STREAK_ACROSS), BANDS, depth=0.62, segments=4,
                        tongues=(2.0, 0.02, 1.2), gap=0.3, width_gap=0.5, head_fractions=(0.2,),
                        tail_fractions=(0.5,))
        parts.append(loft.build(name + "_streak%d" % i, mats))
    return parts


# 123 (the second player's charge cannon, charge 2): a low dark dome with five bright ribs running down it, the middle
# ones highest (as the sprite's stripes: their tops on a dome, columns 1, 3, 5-6, 8 and 10).
RIBBED_DOME = dict(
    outer=[(0.0, 6.95), (1.5, 6.6), (2.6, 5.7), (3.6, 4.7), (4.6, 3.6), (5.4, 2.6), (5.9, 1.4), (6.0, 0.0),
           (6.0, -2.0), (5.8, -4.0), (5.4, -5.6), (4.8, -6.9)],
    inner=[(0.0, -3.1), (1.4, -3.2), (2.4, -3.7), (3.0, -4.5), (3.5, -5.5), (4.0, -6.4), (4.8, -6.9)],
    samples=25, height=((0.0, 0.85), (0.6, 0.75), (0.9, 0.45), (1.0, 0.0)),
    crest=0.25, back=1.0,
    along=((0.0, 8.6), (0.5, 8.0), (0.8, 6.2), (1.0, 3.0)),
    front=0.45, back_drop=0.55, peak=0.2, back_power=1.0,
)
# The ribs: x, the y of their top and of their foot, half-width; their heat from the top (white-green) down.
RIBS = [(-4.5, 3.9, -6.6, 0.62), (-2.5, 5.9, -4.2, 0.62), (0.0, 7.0, -3.2, 0.85), (2.5, 5.9, -4.2, 0.62),
        (4.5, 3.9, -6.6, 0.62)]
RIB_ALONG = ((0.0, 13.0), (0.12, 14.6), (0.4, 12.6), (0.7, 9.0), (1.0, 4.4))
RIB_ACROSS = ((0.0, 2.0), (1.0, 2.6))


def build_ribbed(name):
    mats, cmats = wave_mats("sonic"), core_mats("sonic")
    spec = RIBBED_DOME
    outer, u = arch_path(spec["outer"], spec["samples"])
    inner, _ = arch_path(spec["inner"], spec["samples"])
    wave = Wave(outer, inner, u, height_curve(spec["height"]),
                heat_field(spec["along"], spec["front"], spec["back_drop"], spec["peak"], spec["back_power"]), BANDS,
                crest=spec["crest"], back=spec["back"], gap=0.35)
    parts = [wave.build(name + "_dome", mats)]
    # (each rib's hottest band in the cores' white-green: the core material as one more band)
    rib_bands = BANDS + [(13.4, 0xcf, 0.62)]
    rib_mats = mats + [cmats[0]]
    for i, (x, top, foot, w) in enumerate(RIBS):
        loft = kit.Loft(x, top, foot, kit.curve(((0.0, 0.0), (0.05, w * 0.8), (0.15, w), (0.75, w * 0.85),
                                                  (0.95, w * 0.4), (1.0, 0.0))),
                        kit.loft_heat(RIB_ALONG, RIB_ACROSS), rib_bands, depth=1.9, segments=6,
                        tongues=(2.0, 0.015, 1.2), gap=0.18, width_gap=0.5)
        parts.append(loft.build(name + "_rib%d" % i, rib_mats))
    return parts


# The chevron (shots2 248-251, whole: 48 x 14, x = c + 0.5 - 24 for its columns c, y = 6.5 - r): its upper (front)
# and lower (back) edges' right halves, apex first, ending at the same tip at the cells' bottom; the line is fat at
# its apex and thinner down its arms, brightest a pixel and a half above its lower edge (the sprites' white-green
# 0xcf), a gradient up to its upper edge.
CHEVRON = dict(
    outer=[(0.0, 7.0), (1.4, 6.85), (2.6, 6.15), (4.0, 5.05), (6.0, 3.6), (9.0, 1.55), (12.0, -0.45), (15.0, -2.5),
           (18.0, -4.6), (19.9, -6.05), (19.8, -6.95)],
    inner=[(0.0, 2.05), (1.0, 1.75), (2.2, 1.0), (4.0, 0.0), (6.0, -1.0), (8.0, -2.0), (10.0, -3.0), (12.0, -4.0),
           (14.0, -5.0), (16.0, -6.0), (18.0, -6.85), (19.8, -6.95)],
    samples=49, height=((0.0, 1.6), (0.5, 1.45), (0.88, 1.2), (0.96, 0.8), (1.0, 0.0)),
    crest=0.62, back=0.7,
    along=((0.0, 14.8), (0.2, 14.6), (0.5, 14.2), (0.7, 13.0), (0.85, 11.0), (0.95, 9.2), (1.0, 7.0)),
    front=0.85, back_drop=0.75, peak=0.68, back_power=1.0, core=(0.86, 0.5, 0.3))


def build_chevron(name):
    mats, cmats = wave_mats("sonic"), core_mats("sonic")
    spec = CHEVRON
    outer, us = arch_path(spec["outer"], spec["samples"], smooth=1)
    inner, _ = arch_path(spec["inner"], spec["samples"], smooth=1)
    wave = Wave(outer, inner, us, height_curve(spec["height"]),
                heat_field(spec["along"], spec["front"], spec["back_drop"], spec["peak"], spec["back_power"]), BANDS,
                crest=spec["crest"], back=spec["back"], waves=(6.0, 0.015, 1.9), gap=0.35)
    parts = [wave.build(name + "_wave", mats)]
    c, w, lift = spec["core"]
    n = len(us) - 1
    parts.append(crest_core(name + "_core", wave, spec["peak"], n * (1 - c) / 2, n * (1 + c) / 2, w, lift, CORE_BANDS,
                            cmats, rings=40))
    return parts


# === The models and their lines =======================================================================================
# Lines: (sheet, sprite, yaw, at dx, at dy) for the checks (at= as measured; models.cfg takes them).

def build_double(name):
    mats, cmats = wave_mats("sonic"), core_mats("sonic")
    return build_arch(name + "_o", ARCHES["double_outer"], "sonic", mats, cmats) + \
        build_arch(name + "_i", ARCHES["double_inner"], "sonic", mats, cmats)


def single(key):
    def build(name):
        return build_arch(name, ARCHES[key], "sonic", wave_mats("sonic"), core_mats("sonic"))
    return build


# The sixteen headings of the second player's turret (linkSonicGr: heading k flies k x 22.5 degrees counter-clockwise
# from straight down: yaw = 180 - 22.5 k) and the Sonic Wave's own tilted waves among them.
LINK_SONIC = [85, 242, 131, 303, 47, 284, 150, 223, 66, 224, 149, 283, 9, 302, 130, 243]
HEADINGS = {s: (180.0 - 22.5 * kk) % 360 for kk, s in enumerate(LINK_SONIC)}
# at= (screen pixels, dy down) laying the turned arch on each heading's pixels (fitted with --check: the silhouettes'
# overlap and the crest on the sprite's brightest pixels).
ARCH_AT = {66: (0.0, 0.0), 85: (0.0, 0.0), 223: (0.0, 0.0), 224: (0.0, 0.0), 242: (0.0, 0.0), 243: (0.0, 0.0),
           150: (0.0, 0.0), 149: (0.0, 0.0), 131: (0.0, 0.0), 130: (0.0, 0.0), 284: (0.0, 0.0), 283: (0.0, 0.0),
           303: (0.0, 0.0), 302: (0.0, 0.0), 47: (0.0, 0.0), 9: (0.0, 0.0)}

ONE = {
    "shot_sonic": (single("arch"), [("shots", s, HEADINGS[s]) + ARCH_AT[s] for s in LINK_SONIC], (0.0, 4.6),
                   "the arch"),
    "shot_sonic_2": (single("flat"), [("shots", 63, 0.0, 0.0, 0.0), ("shots", 82, 180.0, 0.0, 0.0)], (0.0, 1.6),
                     "the flat arch"),
    "shot_sonic_3": (build_double, [("shots", 73, 0.0, 0.0, 0.0), ("shots", 16, 270.0, 0.0, -1.0),
                                    ("shots", 54, 90.0, 0.0, -1.0)], (0.0, 3.6), "two arches one inside the other"),
    "shot_sonic_4": (single("slim"), [("shots", 6, 270.0, 0.0, 0.0), ("shots", 44, 90.0, 0.0, 0.0)], (0.0, 2.6),
                     "the slim crescent"),
    "shot_sonic_123": (build_ribbed, [("shots", 123, 0.0, 0.0, 0.0)], (0.0, 5.0), "a dark dome with five bright ribs"),
}

# The pieces: (sheet, sprite, its box in the whole (x0, x1, y0, y1)), the whole's turn and shift after it is built
# apex up (degrees counter-clockwise; then moved), mirrored or not.
WHOLES = {
    "left": dict(build=lambda: build_big("sonic_left", BIG["side"], "sonic"), turn=90.0, shift=(0.0, 0.5),
                 mirror=False, size=(12, 28),
                 pieces=[("shots", 105, (-6.0, 6.0, 0.0, 14.0)), ("shots", 124, (-6.0, 6.0, -14.0, 0.0))]),
    "right": dict(build=lambda: build_big("sonic_right", BIG["side"], "sonic"), turn=90.0, shift=(0.0, 0.5),
                  mirror=True, size=(12, 28),
                  pieces=[("shots", 106, (-6.0, 6.0, 0.0, 14.0)), ("shots", 125, (-6.0, 6.0, -14.0, 0.0))]),
    "arch": dict(build=lambda: build_big("sonic_arch", BIG["up"], "sonic"), turn=0.0, shift=(0.5, 0.0),
                 mirror=False, size=(24, 14),
                 pieces=[("shots", 143, (-12.0, 0.0, -7.0, 7.0)), ("shots", 144, (0.0, 12.0, -7.0, 7.0))]),
    "chevron": dict(build=lambda: build_chevron("sonic_chevron"), turn=0.0, shift=(0.0, 0.0), mirror=False,
                    size=(48, 14),
                    pieces=[("shots2", 248, (-24.0, -12.0, -7.0, 7.0)), ("shots2", 249, (-12.0, 0.0, -7.0, 7.0)),
                            ("shots2", 250, (0.0, 12.0, -7.0, 7.0)), ("shots2", 251, (12.0, 24.0, -7.0, 7.0))]),
}


def piece_name(sheet, sprite):
    return "shot_sonic_%s%d" % ("b" if sheet == "shots2" else "", sprite)


def place(objects, turn, shift, mirror):
    m = Matrix.Translation((shift[0], shift[1], 0.0)) @ Matrix.Rotation(math.radians(turn), 4, "Z")
    if mirror:
        m = Matrix.Scale(-1, 4, (1, 0, 0)) @ m
    for obj in objects:
        obj.data.transform(m)
        if mirror:
            obj.data.flip_normals()
        obj.data.update()


def fit_at(grid, mask, pixels, hot_model, yaw, reach=3.0, hot_weight=0.03):
    """The at= (dx, dy) that lays the model turned yaw on the sprite (yaw kept): the silhouettes' overlap less
    hot_weight times the square of the distance from the model's hot point to the sprite's hottest pixels."""
    import numpy as np
    m = np.array(mask, dtype=float)
    hx, hy = kit.hot_centre(pixels)

    def score(dx, dy):
        cov = kit.placed_coverage(grid, yaw, dx, dy, sub=2)
        iou = np.minimum(cov, m).sum() / max(np.maximum(cov, m).sum(), 1e-6)
        px, py = kit.placed_point(hot_model, yaw, dx, dy)
        d2 = (px - hx) ** 2 + (-py - hy) ** 2
        return iou - hot_weight * d2, iou, math.sqrt(d2)
    best = None
    for dx in np.arange(-reach, reach + 1e-6, 0.25):
        for dy in np.arange(-reach, reach + 1e-6, 0.25):
            s = score(dx, dy)
            if best is None or s[0] > best[0][0]:
                best = (s, dx, dy)
    _, bx, by = best
    for dx in np.arange(bx - 0.25, bx + 0.26, 0.0625):
        for dy in np.arange(by - 0.25, by + 0.26, 0.0625):
            s = score(dx, dy)
            if s[0] > best[0][0]:
                best = (s, dx, dy)
    (_, iou, dist), dx, dy = best
    return float(dx), float(dy), float(iou), float(dist)


def check_one(name, parts, sheets, lines, hot):
    grid = kit.top_coverage(parts)
    for sheet, sprite, yaw, dx, dy in lines:
        mask, pixels = kit.sprite_rows(os.path.join(sheets, sheet + ".png"), sprite)
        kit.print_overlap("%s on %s %d (yaw %g at %g:%g)" % (name, sheet, sprite, yaw, dx, dy),
                          kit.placed_coverage(grid, yaw, dx, dy), mask)
        fdx, fdy, iou, dist = fit_at(grid, mask, pixels, hot, yaw)
        gx, gy = kit.placed_point(hot, yaw, fdx, fdy)
        print("fit %s %s %d: yaw=%g at=%.2f:%.2f (overlap %.3f, hot point %.2f px off; glow at %.1f:%.1f)" % (
            name, sheet, sprite, yaw, fdx, fdy, iou, dist, gx, gy))


def build():
    options = k.args()
    only = set(options["only"].split(",")) if "only" in options else None
    outdir = options.get("outdir", OUTDIR)
    sheets = options.get("check")
    for name, (builder, lines, hot, what) in ONE.items():
        if only is not None and name not in only:
            continue
        k.reset()
        parts = triangulate(builder(name))
        bpy.context.view_layer.update()
        print("== %s (%s): %s" % (name, " ".join("%s %d" % (l[0], l[1]) for l in lines), what))
        if sheets:
            check_one(name, parts, sheets, lines, hot)
        bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
        mk.report(name, parts, os.path.join(outdir, name + ".glb"))
        if "preview" in options:
            view(options["preview"] + name, parts)
    for key, spec in WHOLES.items():
        names = [piece_name(sheet, s) for sheet, s, _ in spec["pieces"]]
        if only is not None and not any(n in only for n in names) and key not in only:
            continue
        k.reset()
        whole = triangulate(spec["build"]())
        place(whole, spec["turn"], spec["shift"], spec["mirror"])
        bpy.context.view_layer.update()
        print("whole %s: %d triangles, height %.2f" % (key, mk.triangles(whole),
                                                       max(v.co.z for o in whole for v in o.data.vertices)))
        w, h = spec["size"]
        if sheets:
            boxes = spec["pieces"]
            m = [[False] * w for _ in range(h)]
            for sheet, s, (x0, x1, y0, y1) in boxes:
                sm = k.sprite_mask(os.path.join(sheets, sheet + ".png"), s, large=False)
                c0, r0 = int(x0 + w / 2), int(h / 2 - y1)
                for r, row in enumerate(sm):
                    for c, v in enumerate(row):
                        if v:
                            m[r0 + r][c0 + c] = True
            mk.compare("whole %s" % key, mk.coverage(whole, w, h), m)
        if "preview" in options:
            bpy.context.scene.view_settings.view_transform = "Standard"
            view(options["preview"] + "shot_sonic_%s_whole" % key, whole, size=(w, h))
        cap = core_mats("sonic")[0]
        cut = {}
        for sheet, s, box in spec["pieces"]:
            cx, cy = (box[0] + box[1]) / 2, (box[2] + box[3]) / 2
            parts = []
            for obj in whole:
                piece = mk.cut(obj, box, cap)
                if piece is None:
                    continue
                piece.data.transform(Matrix.Translation((-cx, -cy, 0.0)))
                piece.name = "%s_%s%d" % (obj.name, "b" if sheet == "shots2" else "", s)
                parts.append(piece)
            cut[(sheet, s)] = parts
        for o in whole + [o for parts in cut.values() for o in parts]:
            o.hide_render = True
        for (sheet, s), parts in cut.items():
            name = piece_name(sheet, s)
            if only is not None and name not in only and key not in only:
                continue
            for o in parts:
                o.hide_render = False
            bpy.context.view_layer.update()  # (the cut pieces' bounds, for the report)
            if sheets:
                mk.compare("%s (%s %d)" % (name, sheet, s), mk.coverage(parts, 12, 14),
                           k.sprite_mask(os.path.join(sheets, sheet + ".png"), s, large=False))
            bpy.context.scene.view_settings.view_transform = "Standard"
            mk.report(name, parts, os.path.join(outdir, name + ".glb"))
            if "preview" in options:
                view(options["preview"] + name, parts)
            for o in parts:
                o.hide_render = True


if __name__ == "__main__":
    build()
