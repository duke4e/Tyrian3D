"""The fireballs (shots sheet sprites 99, 100, 98, 75, 94, 18, 56, 121, 122, 140, 141, 102 and 104, all 1x1: 12 x 14
cells), modelled (2026-10-29, the second round of the energy shots' models after the Pulse-Cannon's pilot,
polish_shot_pulse.py; until then each was drawn as its sprite with volume and the automatic glow). This script also
holds the kit the round's other fire scripts build with (polish_shot_widget.py, polish_shot_megacannon.py,
polish_shot_megapulse.py): Loft (a body along the screen's y on its bands' borders, both sides of its hot part), Dome
(rings round a hot spot), dome_core and core (raised hot cores), build_drop (a head with tongues or drips trailing),
blob_heat (a head's heat as a field), fourier_rim, the bands' materials, the heading fit (fit_heading) and view().

Who fires them (sprite numbers of the shots sheet; ports by their number in the shop's lists, power levels 1-11):
  99   small orange fireball: the Fireball rear (port 18, shop 1:4: power 1-4, 7-8 and 11, both modes, flying down and
       out sideways), the MicroSol option's eight-way burst (special 33, weapon 21), the second player's linked turret
       of rear ports 15, 31 and 36 (weapon 449), and LAVA RUN's turrets (enemy weapon 23 in episode 4, by fire override)
  100  medium orange fireball: the Fireball rear (power 5-8, 10, 11), port 16's option weapon 66
  98   large yellow fireball: the Fireball rear (power 9-11), the NortShip Spreader (port 37, power 8-9: six ways), port
       16's weapon 83, ICE EXIT's turrets (enemy weapon 83)
  75   white-hot fireball flying up, flame tongues trailing: the Mega Cannon (port 3) at power 5 (two), the Phoenix
       Device (sidekick 8, weapon 22: 75 up, 94 down, 18 right, 56 left at once), the MicroSol option 4 (special 34)
  94   the same flying down (yaw 180): the Phoenix Device, BRAINIAC's (enemy weapon 43, episode 4) and AST. CITY's
       (weapon 72, episode 3) turrets
  18   the same flying right (yaw 90), 56 flying left (yaw 270): the Phoenix Device
  121  yellow-white comet flying up and left at 45 degrees (drawn at 321), 122 up and right (drawn at 39): the
       Multi-Cannon front (port 2, first shop: power 7-11, the outer pair of its fan), the MicroSol FrontBlaster
       (sidekick 20, first shop), the BattleShip-Class Firebomb (sidekick 22), the NortShip Spreader (power 6-7)
  140  the comet flying down and left (drawn at 219), 141 down and right (141): the Firebomb, AST. CITY's turrets
       (enemy weapon 72)
  102  a short fat comet flying left, 104 right: the Firebomb (its six ways: 121 122 102 104 140 141)

As the sprites draw them (ramp 7, the fire: 0x70 black-red .. 0x77 red .. 0x7a orange .. 0x7c yellow .. 0x7f white):
- 99 a 6 x 6 ball (columns 3-8, rows 4-9), orange (0x78-0x7b), its hottest pixels (0x7c, 0x7d) up and right of its
  middle. 100 a 10 x 10 ball (columns 1-10, rows 2-11), orange with a bright arc up and right (0x7c) and a darker red
  eye down and left of its middle (0x75-0x77). 98 a 12 x 12 ball (columns 0-11, rows 1-12): yellow-white over most of
  it (0x7d, 0x7e left of the middle), dark red along its top, left and right edges, a bright arc along its bottom.
- 75 a 10 x 9 white-hot ball (rows 0-8: 0x7f over rows 3-6, 0x7e round it, then 0x7c, 0x7b, an orange-red rim) with
  three flame tongues trailing down: one in the middle to row 13 (orange to dark red), short ones at the sides (columns
  2 and 9, rows 9-10), dark gaps between them. 94 is 75 upside down, 18 and 56 the same turned sideways (their tails a
  little shorter, the cell being 12 wide).
- 121 a teardrop 17 pixels long, 6.5 wide at its round head (white 0x7f in it, then yellow, orange), its tail tapering
  to a pixel (orange down the middle, dark red at the edges), drawn at 321 degrees; 122, 140, 141 the same at 39, 219,
  141. 102 a shorter, fatter teardrop (12 long, 9 wide), its head at the left (0x7f at columns 2-3), 104 the same
  pointing right.

The models, built with the pulse's method (polish_shot_pulse.py: half-bodies, round on top and flat underneath, since
the game's camera only ever sees shots from above; palette materials; an idealized heat in bands of ramp 7 whose borders
are the mesh's own rings, so no face is cut; a raised hot core; at most 10 materials):
- the balls (shot_fireball, _2, _3) are domes (Dome): rings round a hot spot up and right of the middle (99, 100) or
  left of it (98), the heat falling from the hot spot to the rim, the rim's heat round the ball two harmonics fitted to
  the sprite's edge pixels (fourier_rim; 98: dark along its top and sides, bright down and right), the bands' borders
  waving a little and swirling round (fire rolling round the ball); a raised core on the hot spot (dome_core: an oval
  patch following the ball's top).
- the flare (shot_fireball_flare, 75; 94, 18, 56 turned) is a ball of fire lofted along the screen's y (Loft), narrowing
  into the middle tongue; its heat a field round the head's middle (blob_heat: white there, falling to the rim in
  rings), capped down the middle tongue as the sprite's middle columns; each band border is two rings of the mesh, one
  in front of the hot part and one behind; the two side tongues small lofts of their own (their roots inside the ball);
  a white core (0x7f in its middle, 0x7e round it) standing out of the head.
- the comets (shot_fireball_comet: 121 122 140 141; shot_fireball_comet_2: 102 104) are teardrops lofted the same way,
  authored head up and turned onto each sprite by its line's yaw= with at= (where the turned model must be moved to lie
  on the sprite's pixels, found by fit_heading: the silhouette's overlap and the hot core on the sprite's hottest
  pixels), a white core in each head.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera; the origin at the
sprite's centre (pixel 6, 7 of the cell: column c is x = c + 0.5 - 6, row r is y = 6.5 - r, its top edge y = 7 - r);
built on z = 0 (the game centres shot models in height on the player's layer). The comets' origin is their own middle.

models.cfg (the shots section; the glow= of each line replaces the automatic glow): see the block's comment; run with
--check to print the silhouettes and the comets' and the flare's fitted yaw= and at=.

Run: Blender -b --factory-startup -P tools/blender/models/shots/polish_shot_fireball.py -- [--only <name,...>]
     [--outdir <dir>] (default assets/models/shots) [--check <sheets dir>] (each model's top view against its sprites
     in <dir>/shots.png, from TYR3D_EXTRACT, and the headings' fit) [--preview <prefix>] (top, three-quarter and
     game-camera views)
"""
import math
import os
import sys

import bmesh
import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
ENEMIES = os.path.join(HERE, "..", "enemies")
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, ENEMIES)
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
import polish_machine_kit as mk  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402
from polish_flame_drop import monotone  # noqa: E402
from polish_launched_flames import lit  # noqa: E402
from polish_shot_pulse import mesh_from_rings, game_view  # noqa: E402

OUTDIR = os.path.join(HERE, "..", "..", "..", "..", "assets", "models", "shots")
TOP = 7.0  # the y of a 1x1 sprite's top edge
FIRE_ROUGHNESS, CORE_ROUGHNESS = 0.5, 0.4


# === The kit ==========================================================================================================

def curve(points):
    """A smooth curve through [(t, value), ...] (t ascending) that never overshoots them."""
    return monotone([p[0] for p in points], [p[1] for p in points])


def materials(prefix, bands, roughness=FIRE_ROUGHNESS):
    """The bands' palette materials: [(lowest heat, palette index, emission strength)] -> [material], each glowing in
    its own colour."""
    return [lit(f"{prefix}_{index:02x}", index, glow, roughness=roughness) for _, index, glow in bands]


def _bisect(f, lo, hi, value, rising):
    """Where f crosses value between lo and hi (f(lo) < value <= f(hi) if rising, else the other way round)."""
    for _ in range(32):
        mid = (lo + hi) / 2
        if (f(mid) >= value) == rising:
            hi = mid
        else:
            lo = mid
    return (lo + hi) / 2


def crossings(f, value, steps=240):
    """Where a profile f(t) on [0, 1] that rises to its peak and then falls crosses value: (rising t, falling t); 0 or
    1 where it starts or ends above the value; both the peak's t where it never reaches it."""
    ts = [i / steps for i in range(steps + 1)]
    fs = [f(t) for t in ts]
    peak = max(range(len(fs)), key=lambda i: fs[i])
    if fs[peak] < value:
        return ts[peak], ts[peak]
    rise = 0.0
    for i in range(peak, 0, -1):
        if fs[i - 1] < value:
            rise = _bisect(f, ts[i - 1], ts[i], value, True)
            break
    fall = 1.0
    for i in range(peak, steps):
        if fs[i + 1] < value:
            fall = _bisect(f, ts[i], ts[i + 1], value, False)
            break
    return rise, fall


def clean(obj, dist=1e-4):
    """Collapses the faces that came out of zero area (rings meeting where a band is missing at some angle)."""
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.dissolve_degenerate(bm, dist=dist, edges=bm.edges[:])
    bm.to_mesh(obj.data)
    bm.free()
    return obj


def ring_sequence(borders, labels, start_band, gap, extra, head_fractions, tail_fractions):
    """The rings of a body built on its bands' borders: borders (curves: a t per angle) in order along it, labels the
    band of the faces after each; start_band the band before the first. Curves lying on the start (t 0 everywhere) or
    the end (t 1) or on the curve before are dropped; rings are added between the start and the first curve (at
    head_fractions of it), between curves further apart than gap (t) or extra(a, b) (any other reason: a curve's width
    changing fast), and between the last curve and the end (tail_fractions of the way). Returns [(curve, band of the
    faces after it)], the band of the faces round the start and the band round the end."""
    kept = []
    band0 = start_band
    for curve_, band in zip(borders, labels):
        if max(curve_) < 1e-4:
            band0 = band  # (on the start)
            continue
        if min(curve_) > 1 - 1e-4:
            continue  # (on the end)
        if kept and max(abs(a - b) for a, b in zip(curve_, kept[-1][0])) < 1e-4:
            kept[-1] = (kept[-1][0], band)
            continue
        kept.append((list(curve_), band))
    if not kept:
        raise ValueError("no rings")
    out = []
    first = kept[0][0]
    for f in head_fractions:
        out.append(([f * t for t in first], band0))
    for i, (line, band) in enumerate(kept):
        out.append((line, band))
        if i + 1 < len(kept):
            following = kept[i + 1][0]
            n = int(max(b - a for a, b in zip(line, following)) / gap)
            if extra is not None:
                n = max(n, extra(line, following))
            for j in range(1, n + 1):
                f = j / (n + 1)
                out.append(([a + (b - a) * f for a, b in zip(line, following)], band))
    last, last_band = kept[-1]
    for f in tail_fractions:
        out.append(([a + (1.0 - a) * f for a in last], last_band))
    return out, band0, last_band


class Loft:
    """A body of fire along the screen's y (head up), round on top and flat underneath (z = 0): x its axis, nose and
    tail the y of its tips; width(t) its half-width at t (0 the nose, 1 the tail), depth its height over its
    half-width (sections are half-ellipses); heat(t, s) the fire's heat at t and s (s = cos of the angle round the top:
    1 the right side, 0 the top, -1 the left side), rising from the nose to its peak and falling to the tail at every s;
    bands [(lowest heat, palette index, emission)] ascending. Its rings are the bands' borders (each band border two
    rings, before and behind the hot part), with rings between them where they lie far apart, so that every face lies
    in one band; the borders wave a little round the top (tongues: (how many across the top, how far they reach (t),
    how much each border's are turned against the one before (radians))."""

    def __init__(self, x, nose, tail, width, heat, bands, depth=0.9, segments=8, tongues=(2.5, 0.03, 1.9),
                 gap=0.17, width_gap=0.7, head_fractions=(0.06, 0.2, 0.45), tail_fractions=(0.45, 0.8), heat_xy=None):
        self.heat_xy = heat_xy  # (x, y) -> heat, in place of heat(t, s) (the heat as a field over the screen)
        self.x, self.nose, self.tail = x, nose, tail
        self.length = nose - tail
        self.width, self.heat, self.bands, self.depth = width, heat, bands, depth
        self.segments, self.tongues, self.gap, self.width_gap = segments, tongues, gap, width_gap
        self.head_fractions, self.tail_fractions = head_fractions, tail_fractions

    def half_width(self, t):
        return max(self.width(min(max(t, 0.0), 1.0)), 0.0)

    def height(self, t):
        return self.half_width(t) * self.depth

    def point(self, t, a):
        w = max(self.half_width(t), 0.02)
        h = max(self.height(t), 0.02 * self.depth)
        return Vector((self.x + w * math.cos(a), self.nose - t * self.length, h * math.sin(a)))

    def top(self, x, y):
        """The height of the body's top at (x, y) (0 outside it)."""
        t = (self.nose - y) / self.length
        if not 0.0 <= t <= 1.0:
            return 0.0
        w = self.half_width(t)
        u = (x - self.x) / w if w > 1e-6 else 2.0
        return self.height(t) * math.sqrt(1.0 - u * u) if abs(u) < 1.0 else 0.0

    def curves(self):
        """[(t per angle, band after)], the band round the nose, the band round the tail."""
        count = self.segments
        angles = [math.pi * j / count for j in range(count + 1)]
        thresholds = [b[0] for b in self.bands[1:]]
        rise = [[0.0] * len(angles) for _ in thresholds]
        fall = [[1.0] * len(angles) for _ in thresholds]
        for j, a in enumerate(angles):
            s = math.cos(a)

            def along(t, s=s):
                if self.heat_xy is not None:
                    return self.heat_xy(self.x + self.half_width(t) * s, self.nose - t * self.length)
                return self.heat(t, s)
            for i, v in enumerate(thresholds):
                rise[i][j], fall[i][j] = crossings(along, v)
        many, reach, turn_ = self.tongues
        for i in range(len(thresholds)):
            for j, a in enumerate(angles):
                closed = fall[i][j] - rise[i][j] < 1e-6
                wave = reach * math.sin(many * a + turn_ * i + self.x * 1.3 + self.nose * 0.7) * math.sin(a) ** 0.5
                if rise[i][j] > 1e-6:
                    rise[i][j] = min(max(rise[i][j] + wave, 0.01), 0.99)
                if fall[i][j] < 1 - 1e-6:
                    fall[i][j] = min(max(fall[i][j] + wave, 0.01), 0.99)
                if closed:
                    fall[i][j] = rise[i][j] = (rise[i][j] if rise[i][j] > 1e-6 else fall[i][j])
        borders = [list(r) for r in rise] + [list(f) for f in reversed(fall)]
        labels = list(range(1, len(thresholds) + 1)) + list(range(len(thresholds) - 1, -1, -1))
        for i in range(1, len(borders)):  # (each ring behind the one before it, at every angle)
            borders[i] = [max(b, p) for b, p in zip(borders[i], borders[i - 1])]

        def extra(a_line, b_line):
            worst = max(abs(self.half_width(tb) - self.half_width(ta)) for ta, tb in zip(a_line, b_line))
            return int(worst / self.width_gap)
        return ring_sequence(borders, labels, 0, self.gap, extra, self.head_fractions, self.tail_fractions)

    def build(self, name, mats):
        count = self.segments
        angles = [math.pi * j / count for j in range(count + 1)]
        curves, nose_band, tail_band = self.curves()
        rings = [[self.point(t, a) for t, a in zip(ts, angles)] for ts, _ in curves]
        bands = [band for _, band in curves[:-1]] + [nose_band, tail_band]
        obj = mesh_from_rings(name, rings, bands, ((self.x, self.nose, 0.0), (self.x, self.tail, 0.0)), mats, 0)
        clean(obj)
        k.recalc_normals(obj)
        return k.smooth(obj, 70)


class Dome:
    """A half-body round about a hot spot (balls): rings round the hot spot (hot, x y) out to its outline, radius(phi)
    the distance from the hot spot to the outline at the angle phi (0 right, counter-clockwise); top(x, y) its height;
    heat(u, phi) the fire's heat at u (0 the hot spot, 1 the outline), falling outwards; bands as Loft's. The rings are
    the bands' borders, waving round the hot spot (tongues: (waves round, how far they reach (u), turn)), rings between
    them where they lie far apart, a fan to the hot spot in its middle and a flat underside (the darkest band's)."""

    def __init__(self, hot, radius, top, heat, bands, segments=24, tongues=(5, 0.04, 1.3), gap=0.2,
                 middle_fractions=(0.35, 0.7), rim_fractions=(0.4, 0.7, 0.88, 1.0), waves=None):
        self.hot, self.radius, self.top_, self.heat, self.bands = hot, radius, top, heat, bands
        self.segments, self.tongues, self.gap = segments, tongues, gap
        self.middle_fractions, self.rim_fractions = middle_fractions, rim_fractions
        self.waves = waves  # (border index, phi, u) -> how far that border moves out there, in place of tongues

    def point(self, u, phi):
        r = u * self.radius(phi)
        x, y = self.hot[0] + r * math.cos(phi), self.hot[1] + r * math.sin(phi)
        return Vector((x, y, self.top_(x, y)))

    def curves(self):
        count = self.segments
        phis = [2 * math.pi * j / count for j in range(count)]
        thresholds = [b[0] for b in self.bands[1:]]
        borders = []
        for v in reversed(thresholds):  # (the hottest border first, nearest the hot spot)
            line = []
            for phi in phis:
                # (heat at 1 - u rises from the rim to the hot spot: where it first reaches v coming in from the rim;
                # 1 where the rim is already that hot, 0 where the hot spot isn't)
                rise, _ = crossings(lambda u, phi=phi: self.heat(1.0 - u, phi), v)
                line.append(1.0 - rise)
            borders.append(line)
        many, reach, turn_ = self.tongues
        for i, line in enumerate(borders):
            for j, phi in enumerate(phis):
                if 1e-6 < line[j] < 1 - 1e-6:
                    if self.waves is not None:
                        move = self.waves(i, phi, line[j])
                    else:
                        move = reach * math.sin(many * phi + turn_ * i)
                    line[j] = min(max(line[j] + move, 0.02), 0.995)
        for i in range(1, len(borders)):
            borders[i] = [max(b, p) for b, p in zip(borders[i], borders[i - 1])]
        top_band = len(self.bands) - 1
        labels = list(range(top_band - 1, -1, -1))
        return ring_sequence(borders, labels, top_band, self.gap, None, self.middle_fractions, self.rim_fractions)

    def build(self, name, mats, under=0):
        count = self.segments
        phis = [2 * math.pi * j / count for j in range(count)]
        curves, middle_band, rim_band = self.curves()
        verts, faces, fmats = [], [], []
        rings = []
        for ts, _ in curves:
            rings.append(len(verts))
            verts += [self.point(u, phi) for u, phi in zip(ts, phis)]
        centre = len(verts)
        verts.append(Vector((self.hot[0], self.hot[1], self.top_(*self.hot))))
        bottom = len(verts)
        verts.append(Vector((self.hot[0], self.hot[1], 0.0)))
        for j in range(count):
            jj = (j + 1) % count
            faces.append((centre, rings[0] + j, rings[0] + jj))
            fmats.append(middle_band)
        for i in range(len(rings) - 1):
            a, b = rings[i], rings[i + 1]
            for j in range(count):
                jj = (j + 1) % count
                faces.append((a + j, b + j, b + jj, a + jj))
                fmats.append(curves[i][1])
        last = rings[-1]
        for j in range(count):
            jj = (j + 1) % count
            faces.append((bottom, last + jj, last + j))
            fmats.append(under)
        obj = k.mesh_object(name, verts, faces)
        for m in mats:
            obj.data.materials.append(m)
        for poly, m in zip(obj.data.polygons, fmats):
            poly.material_index = m
        clean(obj)
        k.recalc_normals(obj)
        return k.smooth(obj, 70)


def ellipse_dome(cx, cy, rx, ry, height, power=0.5):
    """A dome over an ellipse: its top (x, y) -> height, and its outline as seen from a point (radius(phi) about
    that point)."""
    def top(x, y):
        rho2 = ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2
        return height * max(0.0, 1.0 - rho2) ** power

    def radius_from(px, py):
        def radius(phi):
            dx, dy = math.cos(phi), math.sin(phi)
            # |p + r d - c| on the ellipse: a r^2 + b r + c = 0
            ex, ey = (px - cx) / rx, (py - cy) / ry
            ax, ay = dx / rx, dy / ry
            a = ax * ax + ay * ay
            b = 2 * (ex * ax + ey * ay)
            c = ex * ex + ey * ey - 1.0
            return (-b + math.sqrt(max(b * b - 4 * a * c, 0.0))) / (2 * a)
        return radius
    return top, radius_from


def dome_core(name, centre, rx, ry, lift, host_top, bands, mats, segments=16, tongues=(3, 0.04, 1.0)):
    """A raised core on a dome (or any body): an oval patch round centre (half-axes rx, ry) standing lift out of
    host_top at its middle and meeting it at its rim; bands [(from u, palette index, emission)] from its middle out
    (u: 0 its middle, 1 its rim)."""
    cx, cy = centre
    oval_top, radius_from = ellipse_dome(cx, cy, rx, ry, lift)

    def top(x, y):
        return host_top(x, y) + oval_top(x, y)

    def heat(u, phi):
        return 1.0 - u
    # (as Dome bands: (lowest heat, index, emission) ascending; heat 1 - u)
    outward = list(reversed(bands))
    dome_bands = [(-99.0 if i == 0 else 1.0 - outward[i - 1][0], b[1], b[2]) for i, b in enumerate(outward)]
    dome = Dome(centre, radius_from(cx, cy), top, heat, dome_bands, segments=segments, tongues=tongues, gap=0.3,
                middle_fractions=(0.45,), rim_fractions=(0.45, 0.8, 1.0))
    return dome.build(name, list(reversed(mats)), under=0)


def core(name, x, front, length, w0, lift, host_top, bands, mats, cap=0.3, taper=0.9, ends="drop", segments=6,
         rings=(0.04, 0.15, 0.32, 0.5, 0.66, 0.85)):
    """A core of plasma standing out of a body's top (the pulse's wedge, generalized): a teardrop along the screen's y
    from front (y) back over length, round at its front (cap: the fraction of its length the round front takes) and
    tapering behind (ends "drop"), round at both ends ("capsule") or pointed at both ("spindle"); w0 its half-width,
    lift how far it stands out of host_top(x, y) at its middle line; bands [(from t, palette index, emission)] along it,
    front first."""
    ts = sorted(set(rings) | {b[0] for b in bands[1:]} | ({1 - r for r in rings} if ends != "drop" else set()))
    angles = [math.pi * j / segments for j in range(segments + 1)]

    def shape(t):
        if ends == "spindle":  # (pointed at both ends, full in its middle)
            return math.sin(math.pi * min(max(t, 0.0), 1.0)) ** 0.6
        if t < cap:
            return math.sqrt(max(0.0, 1.0 - (1.0 - t / cap) ** 2))
        if ends == "capsule":
            return math.sqrt(max(0.0, 1.0 - (1.0 - (1.0 - t) / cap) ** 2)) if t > 1 - cap else 1.0
        return ((1.0 - t) / (1.0 - cap)) ** taper
    out = []
    for t in ts:
        y = front - t * length
        f = shape(t)
        w = max(w0 * f, 0.03)
        h = host_top(x, y) + lift * f
        out.append([Vector((x + w * math.cos(a), y, h * math.sin(a))) for a in angles])

    def band_at(t):
        return max(i for i, b in enumerate(bands) if t >= b[0] - 1e-9)
    # (bands may repeat a material: one slot each)
    slots = []
    for m in mats:
        if m not in slots:
            slots.append(m)
    slot = [slots.index(m) for m in mats]
    faces = [slot[band_at((a + b) / 2)] for a, b in zip(ts[:-1], ts[1:])] + [slot[0], slot[-1]]
    obj = mesh_from_rings(name, out, faces, ((x, front, 0.0), (x, front - length, 0.0)), slots, slot[-1])
    clean(obj)
    k.recalc_normals(obj)
    return k.smooth(obj, 80)


# --- Previews and checks ----------------------------------------------------------------------------------------------

def view(prefix, objects, size=(12, 14)):
    """The pulse's game_view (the top and three-quarter views, then the game's camera: 20 degrees from straight down,
    lit by the game's sun) framing size (game pixels) instead of a 1x1 sprite's cell; only these objects."""
    if tuple(size) == (12, 14):
        return game_view(prefix, objects)
    scale = max(size) / 14.0
    mk.preview(prefix, objects, size=size, scale=max(8, int(32 / scale)), distance=0.42 * scale)
    scene = bpy.context.scene
    hidden = [o for o in scene.objects if o.type == "MESH" and o not in objects and not o.hide_render]
    for o in hidden:
        o.hide_render = True
    data = bpy.data.cameras.new("game")
    data.type = "ORTHO"
    data.ortho_scale = 16.0 * scale
    cam = bpy.data.objects.new("game", data)
    tilt = math.radians(20.0)
    cam.location = (0.0, -60.0 * math.sin(tilt), 60.0 * math.cos(tilt))
    cam.rotation_euler = (tilt, 0.0, 0.0)
    scene.collection.objects.link(cam)
    sun = bpy.data.lights.new("game_sun", "SUN")
    sun.energy = 3.0
    sun_obj = bpy.data.objects.new("game_sun", sun)
    sun_obj.rotation_euler = Vector((0.6, -0.6, -1.0)).to_track_quat("-Z", "Y").to_euler()
    scene.collection.objects.link(sun_obj)
    scene.camera = cam
    scene.render.resolution_x = scene.render.resolution_y = 512
    scene.render.filepath = prefix + "_game.png"
    bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(cam)
    bpy.data.objects.remove(sun_obj)
    for o in hidden:
        o.hide_render = False


def sprite_rows(sheet_png, sprite):
    """A 1x1 sprite's pixels: (mask rows, [(x, y, shade)] in model coordinates) from <sheets>/<sheet>.png and .idx."""
    sys.path.insert(0, os.path.join(HERE, "..", ".."))
    from sprite_profile import sprite_indices
    rows = sprite_indices(sheet_png, sprite, large=False)
    mask = [[i is not None for i in row] for row in rows]
    pixels = [(c + 0.5 - 6, 6.5 - r, i & 15) for r, row in enumerate(rows) for c, i in enumerate(row) if i is not None]
    return mask, pixels


def hot_centre(pixels, within=3):
    """The middle of a sprite's hottest pixels: those within `within` shades of its hottest, weighted by the square of
    how close they come to it."""
    top = max(s for _, _, s in pixels)
    hot = [(x, y, (s - (top - within)) ** 2) for x, y, s in pixels if s > top - within]
    total = sum(w for _, _, w in hot)
    return sum(x * w for x, _, w in hot) / total, sum(y * w for _, y, w in hot) / total


def top_coverage(objects, half=16, supersample=8):
    """The objects' top view as a fine grid of coverage (alpha; rows from the top, y = half down to -half) over
    [-half, half]^2, supersample cells a pixel (mk.coverage's render, its alpha kept at full resolution)."""
    import numpy as np
    scene = bpy.context.scene
    hidden = {}
    for obj in scene.objects:
        if obj.type == "MESH":
            hidden[obj.name] = obj.hide_render
            obj.hide_render = obj not in objects
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.film_transparent = True
    scene.render.resolution_x = scene.render.resolution_y = 2 * half * supersample
    scene.render.resolution_percentage = 100
    data = bpy.data.cameras.new("fine_check")
    data.type = "ORTHO"
    data.ortho_scale = 2 * half
    data.clip_end = 1000
    cam = bpy.data.objects.new("fine_check", data)
    cam.location = (0.0, 0.0, 300.0)
    scene.collection.objects.link(cam)
    scene.camera = cam
    path = os.path.join(bpy.app.tempdir or "/tmp", "fine_check.png")
    scene.render.filepath = path
    bpy.ops.render.render(write_still=True)
    image = bpy.data.images.load(path)
    rw, rh = image.size
    alpha = np.array(image.pixels[:]).reshape(rh, rw, 4)[::-1, :, 3].copy()
    bpy.data.images.remove(image)
    bpy.data.objects.remove(cam)
    for obj in scene.objects:
        if obj.name in hidden:
            obj.hide_render = hidden[obj.name]
    return alpha, half, supersample


def placed_coverage(grid, yaw, dx, dy, sub=4):
    """The coverage of each pixel of a 12 x 14 cell by the model turned yaw degrees clockwise and moved dx, dy (screen
    pixels, dy down), from top_coverage's grid."""
    import numpy as np
    cov, half, ss = grid
    c = np.arange(12 * sub) / sub + 0.5 / sub
    r = np.arange(14 * sub) / sub + 0.5 / sub
    qx, qy = np.meshgrid(c - 6.0, 7.0 - r)
    qx, qy = qx - dx, qy + dy
    th = math.radians(yaw)
    mx = qx * math.cos(th) - qy * math.sin(th)
    my = qx * math.sin(th) + qy * math.cos(th)
    col = np.floor((mx + half) * ss).astype(int)
    row = np.floor((half - my) * ss).astype(int)
    inside = (col >= 0) & (col < cov.shape[1]) & (row >= 0) & (row < cov.shape[0])
    v = np.where(inside, cov[np.clip(row, 0, cov.shape[0] - 1), np.clip(col, 0, cov.shape[1] - 1)], 0.0)
    return v.reshape(14, sub, 12, sub).mean(axis=(1, 3))


def fit_heading(grid, mask, pixels, hot_model, yaw0, spread=10, reach=3.0, hot_weight=0.03):
    """The yaw (degrees, clockwise) and at= (dx, dy: screen pixels, dy down) that lay the model on the sprite: the
    silhouettes' overlap (soft intersection over union), less hot_weight times the square of the distance between the
    model's hot point (hot_model, model coordinates) turned and moved and the sprite's hottest pixels. Returns
    (yaw, dx, dy, overlap, hot distance)."""
    import numpy as np
    m = np.array(mask, dtype=float)
    hx, hy = hot_centre(pixels)

    def score(yaw, dx, dy):
        cov = placed_coverage(grid, yaw, dx, dy, sub=2)
        iou = np.minimum(cov, m).sum() / max(np.maximum(cov, m).sum(), 1e-6)
        th = math.radians(yaw)
        px = hot_model[0] * math.cos(th) + hot_model[1] * math.sin(th) + dx
        py = -hot_model[0] * math.sin(th) + hot_model[1] * math.cos(th) - dy
        d2 = (px - hx) ** 2 + (py - hy) ** 2
        return iou - hot_weight * d2, iou, math.sqrt(d2)
    best = None
    steps = np.arange(-reach, reach + 1e-6, 0.5)
    for yaw in range(int(yaw0 - spread), int(yaw0 + spread) + 1, 2):
        for dx in steps:
            for dy in steps:
                s = score(yaw, dx, dy)
                if best is None or s[0] > best[0][0]:
                    best = (s, yaw, dx, dy)
    _, yaw, dx, dy = best
    for yaw_ in np.arange(yaw - 2, yaw + 2.01, 0.5):
        for dx_ in np.arange(dx - 0.5, dx + 0.51, 0.125):
            for dy_ in np.arange(dy - 0.5, dy + 0.51, 0.125):
                s = score(yaw_, dx_, dy_)
                if s[0] > best[0][0]:
                    best = (s, yaw_, dx_, dy_)
    (_, iou, dist), yaw, dx, dy = best
    return float(yaw) % 360, float(dx), float(dy), float(iou), float(dist)


def print_overlap(label, cov, mask):
    """The overlap (intersection over union at half coverage) and its map ('#' both, '+' the model only, '-' the
    sprite only)."""
    h, w = len(mask), len(mask[0])
    both = sum(cov[y][x] >= 0.5 and mask[y][x] for y in range(h) for x in range(w))
    either = sum(cov[y][x] >= 0.5 or mask[y][x] for y in range(h) for x in range(w))
    print("silhouette overlap %s: %.3f" % (label, both / max(either, 1)))
    for y in range(h):
        print("".join("#" if cov[y][x] >= 0.5 and mask[y][x] else "+" if cov[y][x] >= 0.5 else "-" if mask[y][x]
                      else "." for x in range(w)))
    return both / max(either, 1)


def placed_point(point, yaw, dx, dy):
    """A model point (x, y) turned yaw degrees clockwise and moved dx, dy: where it lies on the screen, as glow=
    takes it (dx, dy from the sprite's centre, dy down)."""
    th = math.radians(yaw)
    x = point[0] * math.cos(th) + point[1] * math.sin(th) + dx
    y = -point[0] * math.sin(th) + point[1] * math.cos(th) - dy
    return x, -y


def check_lines(name, parts, sheet_png, lines, hot_model=None, fit=False):
    """Each of the model's shot lines [(sprite, yaw, dx, dy)] against its sprite: the overlap map, where the model's hot
    point lies (screen pixels from the sprite's centre, for glow=) against the sprite's hottest pixels; with fit, the
    yaw and at= that fit best."""
    grid = top_coverage(parts)
    for sprite, yaw, dx, dy in lines:
        mask, pixels = sprite_rows(sheet_png, sprite)
        print_overlap("%s on %d (yaw %g at %g:%g)" % (name, sprite, yaw, dx, dy), placed_coverage(grid, yaw, dx, dy),
                      mask)
        hx, hy = hot_centre(pixels)
        gx, gy = placed_point(hot_model or (0.0, 0.0), yaw, dx, dy)
        print("hot %s %d: the model's at %.2f:%.2f, the sprite's at %.2f:%.2f (screen, dy down)" % (
            name, sprite, gx, gy, hx, -hy))
        if fit:
            fy, fdx, fdy, iou, dist = fit_heading(grid, mask, pixels, hot_model or (0.0, 0.0), yaw)
            print("fit %s %d: yaw=%.1f at=%.2f:%.2f (overlap %.3f, hot point %.2f px off)" % (name, sprite, fy, fdx,
                                                                                               fdy, iou, dist))


# === The fireballs ====================================================================================================

def ball_heat(centre, rim, fall=1.35, swirl=(0.0, 1, 0.0, 0.0)):
    """A ball's heat: centre at the hot spot, rim(phi) at the outline, falling between as 1 - (1 - u)^fall (fall > 1:
    the hot middle wider); a swirl (strength, arms, turn per unit of u, phase) bending the bands round as they go
    out."""
    strength, arms, turn_, phase = swirl

    def heat(u, phi):
        g = 1.0 - (1.0 - min(max(u, 0.0), 1.0)) ** fall
        h = centre - (centre - rim(phi)) * g
        return h + strength * math.sin(arms * phi + turn_ * u + phase) * math.sin(math.pi * min(u, 1.0)) * g
    return heat


def fourier_rim(a0, a1=0.0, p1=0.0, a2=0.0, p2=0.0):
    """The rim's heat round a ball as two harmonics: a0, plus a1 at its brightest p1 (degrees counter-clockwise from
    right), plus a2 brightest along p2 and p2 + 180 (rimfit's least-squares fit to the sprite's edge pixels)."""
    def rim(phi):
        return (a0 + a1 * math.cos(phi - math.radians(p1)) + a2 * math.cos(2 * (phi - math.radians(p2))))
    return rim


def rim_curve(points):
    """The rim's heat round a ball: [(angle in degrees, heat)] round the circle (periodic, smooth)."""
    pts = sorted(points)
    xs = [p[0] - 360 for p in pts] + [p[0] for p in pts] + [p[0] + 360 for p in pts]
    ys = [p[1] for p in pts] * 3
    f = monotone(xs, ys)
    return lambda phi: f(math.degrees(phi) % 360)


# The balls: (sprite, the ball's middle and radius, its height over its radius, the hot spot, the heat there and round
# the rim (fourier_rim: fitted to the sprite's edge pixels), the fall, the swirl, the bands, the core (its half-axes
# across and along, lift, bands from its middle out)).
BALLS = {
    "shot_fireball": dict(
        sprite=99, centre=(0.0, 0.0), radius=3.05, depth=0.84, hot=(0.55, 0.75),
        heat=12.4, rim=fourier_rim(8.6, 0.6, 45.0), fall=1.25,
        swirl=(0.25, 2, 2.2, 0.6), tongues=(5, 0.035, 1.3), segments=20,
        bands=[(-99.0, 0x77, 0.36), (8.0, 0x78, 0.42), (8.9, 0x79, 0.46), (9.8, 0x7a, 0.5), (10.8, 0x7b, 0.52)],
        core=(1.1, 2.2, 0.32, ((0.0, 0x7d, 0.6), (0.45, 0x7c, 0.58))),
        what="a small orange fireball"),
    "shot_fireball_2": dict(
        sprite=100, centre=(0.0, 0.0), radius=5.05, depth=0.8, hot=(1.25, 1.35),
        heat=12.2, rim=fourier_rim(8.5, 0.5, 45.0), fall=1.1, swirl=(0.45, 2, 2.6, 2.2), tongues=(6, 0.035, 1.3),
        segments=24,
        bands=[(-99.0, 0x76, 0.34), (7.4, 0x77, 0.38), (8.3, 0x78, 0.42), (9.1, 0x79, 0.46), (9.9, 0x7a, 0.5),
               (10.8, 0x7b, 0.52)],
        core=(1.6, 3.2, 0.38, ((0.0, 0x7d, 0.6), (0.45, 0x7c, 0.58))),
        what="a medium orange fireball"),
    "shot_fireball_3": dict(
        sprite=98, centre=(0.0, 0.0), radius=6.05, depth=0.78, hot=(-0.7, 0.45),
        heat=14.6, rim=fourier_rim(6.4, 3.0, 303.0, 1.6, 124.0), fall=1.55, swirl=(0.5, 2, 2.4, 0.4),
        tongues=(7, 0.03, 1.3), segments=28,
        bands=[(-99.0, 0x73, 0.26), (4.6, 0x75, 0.31), (6.4, 0x77, 0.38), (8.0, 0x79, 0.46), (9.4, 0x7a, 0.5),
               (10.7, 0x7b, 0.52), (11.9, 0x7c, 0.56), (13.0, 0x7d, 0.58)],
        core=(2.2, 4.4, 0.42, ((0.0, 0x7f, 0.62), (0.4, 0x7e, 0.6))),
        what="a large yellow fireball"),
}


def build_ball(name, spec):
    cx, cy = spec["centre"]
    r = spec["radius"]
    top, radius_from = ellipse_dome(cx, cy, r, r, r * spec["depth"])
    hot = spec["hot"]
    heat = ball_heat(spec["heat"], spec["rim"], spec["fall"], spec["swirl"])
    dome = Dome(hot, radius_from(*hot), top, heat, spec["bands"], segments=spec["segments"], tongues=spec["tongues"])
    fire = materials("fireball_fire", spec["bands"])
    parts = [dome.build(name + "_fire", fire)]
    w, length, lift, cbands = spec["core"]
    cmats = materials("fireball_core", cbands, CORE_ROUGHNESS)
    parts.append(dome_core(name + "_core", hot, w, length / 2, lift, top, cbands, cmats))
    return parts


# --- The flare (75) and the comets ------------------------------------------------------------------------------------

def loft_heat(along, across, middle=0.0, power=2.0):
    """A body's heat: along(t) on its middle line (at s = middle), less across(t) times |s - middle| to the power."""
    a, c = curve(along), curve(across)

    def heat(t, s):
        return a(t) - c(t) * min(abs(s - middle), 1.3) ** power
    return heat


def blob_heat(centre, rx, ry_up, ry_down, profile, below=None):
    """A head's heat as a field: profile(d) of the distance d from centre, measured in half-axes (rx across, ry_up
    above the centre, ry_down below it: 1 on the head's rim), never more than below(y) (the tail's or drips' heat down
    the screen: [(y, heat)] ascending in y, the heat at any y above the last unbounded)."""
    f = curve(profile)
    g = curve(below) if below is not None else None
    top_y = below[-1][0] if below is not None else None
    cx, cy = centre

    def heat(x, y):
        dy = (y - cy) / (ry_up if y > cy else ry_down)
        h = f(math.hypot((x - cx) / rx, dy))
        if g is not None and y < top_y:
            h = min(h, g(y))
        return h
    return heat


FLARE_BANDS = [(-99.0, 0x72, 0.22), (3.0, 0x74, 0.26), (5.0, 0x76, 0.33), (7.0, 0x78, 0.4), (8.8, 0x7a, 0.48),
               (10.3, 0x7b, 0.52), (11.6, 0x7c, 0.56), (12.8, 0x7d, 0.58)]
FLARE_CORE_BANDS = ((0.0, 0x7f, 0.62), (0.6, 0x7e, 0.6))

# 75 as drawn: the head's tip at row 0's top edge (y 7), the middle tongue's at row 13's bottom edge (y -7); its
# half-width (t: 0 the tip, 1 the tongue's tip), its heat along its middle and less towards its sides.
FLARE = dict(
    nose=7.0, tail=-7.0, depth=0.86,
    width=((0.0, 0.0), (0.012, 1.6), (0.036, 2.9), (0.09, 3.9), (0.16, 4.6), (0.24, 4.95), (0.36, 5.0), (0.5, 4.95),
           (0.58, 4.6), (0.635, 3.6), (0.68, 2.6), (0.75, 2.05), (0.82, 1.7), (0.89, 1.15), (0.95, 0.7), (1.0, 0.0)),
    # the heat: white round the head's middle (2 above the sprite's centre), falling to its rim (half-axes 5 across,
    # 5 up, 7 down), and down the middle tongue (by y) as the sprite's middle columns
    heat=blob_heat((0.0, 2.0), 5.0, 5.0, 7.0,
                   ((0.0, 15.0), (0.45, 15.0), (0.6, 13.6), (0.75, 11.2), (0.9, 8.2), (1.0, 6.2), (1.1, 3.2),
                    (1.3, 1.5), (2.0, 1.0)),
                   ((-7.0, 1.5), (-6.5, 2.0), (-5.5, 3.0), (-4.5, 5.0), (-3.5, 9.0), (-2.5, 12.0), (-1.5, 13.5),
                    (-0.5, 99.0))),
    # the side tongues: x, the y of their root (inside the ball) and tip, half-width, heat along (root .. tip)
    tongues=[(-3.55, -0.2, -4.05, 0.72), (3.55, -0.2, -4.05, 0.72)],
    tongue_along=((0.0, 9.5), (0.45, 8.6), (0.7, 7.2), (0.85, 5.6), (1.0, 4.0)),
    tongue_across=((0.0, 1.5), (1.0, 2.0)),
    # the core: its middle x, y, half-axes, lift
    core=(0.0, 2.05, 2.25, 2.45, 0.45),
)


def tongue_width(w):
    """A tongue's (or drip's) half-width along it: round where it leaves the body, tapering to its tip."""
    return curve(((0.0, 0.0), (0.06, w * 0.7), (0.2, w), (0.55, w * 0.85), (0.85, w * 0.45), (1.0, 0.0)))


def build_drop(name, spec, prefix, bands, core_bands):
    """A head of fire (or plasma) with tongues or drips trailing behind it: the body (Loft: the head, narrowing into
    the middle tongue), the side tongues (small Lofts whose roots lie inside the body: [(x, root y, tip y, half-width,
    their heat along (root .. tip), or None for the spec's)]), a raised core (dome_core: its middle x, y, half-axes,
    lift) and beads (spec "beads": [(x, y, half-axes, lift, bands from the middle out)]: hotter spots on the body)."""
    fire = materials(prefix + "_fire", bands)
    field = spec.get("heat")
    body = Loft(spec.get("x", 0.0), spec["nose"], spec["tail"], curve(spec["width"]),
                None if field is not None else loft_heat(spec["along"], spec["across"]), bands, depth=spec["depth"],
                segments=spec.get("segments", 12), tongues=spec.get("waves", (2.5, 0.025, 1.9)), gap=0.12,
                width_gap=0.6, heat_xy=field)
    parts = [body.build(name + "_fire", fire)]
    for i, tongue_spec in enumerate(spec["tongues"]):
        x, root, tip, w = tongue_spec[:4]
        along = tongue_spec[4] if len(tongue_spec) > 4 and tongue_spec[4] is not None else spec["tongue_along"]
        tongue = Loft(x, root, tip, tongue_width(w), loft_heat(along, spec["tongue_across"]), bands, depth=0.85,
                      segments=6, tongues=(2.0, 0.02, 1.2), gap=0.2, width_gap=0.5)
        parts.append(tongue.build(name + "_tongue%d" % i, fire))
    if spec.get("core") is not None:
        cx, cy, rx, ry, lift = spec["core"]
        cmats = materials(prefix + "_core", core_bands, CORE_ROUGHNESS)
        parts.append(dome_core(name + "_core", (cx, cy), rx, ry, lift, body.top, core_bands, cmats))
    for i, (cx, cy, rx, ry, lift, bead_bands) in enumerate(spec.get("beads", ())):
        # (hotter beads of fire on the body, in its own bands' materials)
        parts.append(dome_core(name + "_bead%d" % i, (cx, cy), rx, ry, lift, body.top, bead_bands,
                               materials(prefix + "_fire", bead_bands), segments=12, tongues=(3, 0.0, 1.0)))
    return parts


def build_flare(name):
    return build_drop(name, FLARE, "fireball", FLARE_BANDS, FLARE_CORE_BANDS)


COMET_BANDS = [(-99.0, 0x74, 0.26), (5.2, 0x76, 0.33), (7.0, 0x78, 0.4), (8.6, 0x79, 0.46), (9.8, 0x7a, 0.5),
               (11.0, 0x7b, 0.52), (12.2, 0x7c, 0.56), (13.2, 0x7d, 0.58)]
COMET_CORE_BANDS = ((0.0, 0x7f, 0.62), (0.5, 0x7e, 0.6))

# The comets, authored head up round their own middle: their length, half-width, heat (as FLARE) and core.
COMETS = {
    "shot_fireball_comet": dict(
        length=16.7, depth=0.88,
        width=((0.0, 0.0), (0.012, 1.1), (0.035, 2.1), (0.08, 2.95), (0.14, 3.45), (0.2, 3.6), (0.34, 3.55), (0.5, 3.1),
               (0.62, 2.6), (0.74, 2.0), (0.86, 1.3), (0.95, 0.65), (1.0, 0.0)),
        along=((0.0, 6.8), (0.07, 10.6), (0.14, 13.4), (0.21, 14.8), (0.27, 15.0), (0.36, 14.8), (0.46, 13.5),
               (0.57, 12.2), (0.69, 10.5), (0.8, 8.6), (0.9, 6.6), (1.0, 4.6)),
        across=((0.0, 3.0), (0.12, 6.0), (0.27, 9.0), (0.45, 7.8), (0.65, 5.6), (0.85, 4.0), (1.0, 2.5)),
        core=(0.15, 6.4, 1.8, 0.42),
        what="a comet"),
    "shot_fireball_comet_2": dict(
        length=12.0, depth=0.86,
        width=((0.0, 0.0), (0.012, 1.3), (0.035, 2.3), (0.08, 3.1), (0.14, 3.7), (0.22, 4.15), (0.32, 4.35),
               (0.45, 4.3), (0.55, 3.95), (0.65, 3.3), (0.75, 2.55), (0.85, 1.75), (0.93, 0.95), (1.0, 0.0)),
        along=((0.0, 5.5), (0.06, 8.8), (0.14, 12.6), (0.22, 14.8), (0.3, 15.0), (0.39, 14.0), (0.48, 13.0),
               (0.57, 12.0), (0.65, 11.0), (0.73, 10.0), (0.81, 8.8), (0.89, 7.0), (0.95, 5.2), (1.0, 4.0)),
        across=((0.0, 3.0), (0.14, 7.5), (0.28, 10.5), (0.47, 8.5), (0.66, 6.5), (0.85, 4.5), (1.0, 2.5)),
        core=(0.16, 4.2, 2.05, 0.42),
        what="a short fat comet"),
}


def comet_nose(spec):
    """The nose's y that puts the comet's area centre on the origin."""
    w = curve(spec["width"])
    n = 400
    area = sum(w((i + 0.5) / n) for i in range(n))
    centre_t = sum((i + 0.5) / n * w((i + 0.5) / n) for i in range(n)) / area
    return centre_t * spec["length"]


def build_comet(name, spec):
    nose = comet_nose(spec)
    fire = materials("fireball_fire", COMET_BANDS)
    body = Loft(0.0, nose, nose - spec["length"], curve(spec["width"]), loft_heat(spec["along"], spec["across"]),
                COMET_BANDS, depth=spec["depth"], segments=10, tongues=(2.5, 0.025, 1.9), gap=0.12, width_gap=0.6)
    parts = [body.build(name + "_fire", fire)]
    behind, length, w, lift = spec["core"]
    cmats = materials("fireball_core", COMET_CORE_BANDS, CORE_ROUGHNESS)
    parts.append(core(name + "_core", 0.0, nose - behind * spec["length"], length, w, lift, body.top,
                      COMET_CORE_BANDS, cmats, cap=0.4, taper=0.85))
    return parts


def comet_hot(spec):
    """The comet's hot point (model coordinates): the middle of its core's white front."""
    nose = comet_nose(spec)
    behind, length, _, _ = spec["core"]
    return 0.0, nose - behind * spec["length"] - 0.25 * length


# The models: name -> (builder, its shot lines [(sprite, yaw, dx, dy)] for the checks, its hot point for the fit).
# The comets' and the flare's turned lines: yaw= and at= from fit_heading (--check prints them).
LINES = {
    "shot_fireball": [(99, 0, 0, 0)],
    "shot_fireball_2": [(100, 0, 0, 0)],
    "shot_fireball_3": [(98, 0, 0, 0)],
    "shot_fireball_flare": [(75, 0, 0, 0), (94, 180, 0, 0), (18, 90, -1.6, -1.0), (56, 270, 1.6, -1.0)],
    "shot_fireball_comet": [(121, 321.5, -0.12, -0.38), (122, 38.5, 0.12, -0.38), (140, 218.5, -0.12, 0.38),
                            (141, 141.5, 0.12, 0.38)],
    "shot_fireball_comet_2": [(102, 270, -0.75, -0.5), (104, 90, 0.75, -0.5)],
}
FIT = {"shot_fireball_flare", "shot_fireball_comet", "shot_fireball_comet_2"}


def build_model(name):
    if name in BALLS:
        return build_ball(name, BALLS[name])
    if name == "shot_fireball_flare":
        return build_flare(name)
    return build_comet(name, COMETS[name])


def hot_point(name):
    if name in COMETS:
        return comet_hot(COMETS[name])
    if name == "shot_fireball_flare":
        return FLARE["core"][:2]
    return BALLS[name]["hot"]


def build():
    options = k.args()
    only = set(options["only"].split(",")) if "only" in options else None
    outdir = options.get("outdir", OUTDIR)
    for name in LINES:
        if only is not None and name not in only:
            continue
        k.reset()
        parts = triangulate(build_model(name))
        bpy.context.view_layer.update()
        print(f"== {name}: shots {' '.join(str(line[0]) for line in LINES[name])}")
        if "check" in options:
            check_lines(name, parts, os.path.join(options["check"], "shots.png"), LINES[name], hot_point(name),
                        fit=name in FIT)
        bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
        mk.report(name, parts, os.path.join(outdir, name + ".glb"))
        if "preview" in options:
            view(options["preview"] + name, parts)


if __name__ == "__main__":
    build()
