"""The Xega Ball (option shape 21: 55 x 54 pixels), modelled (2026-10-30, the fifth round of the shots' models: the big
shots some weapons draw blended from the option shapes; until then it went into the shots' captured layer and showed in
the 3D view as a flat image of the screen's pixels, a dark red pixelled disc lying on the shots' layer).

Who fires it: the special Xega Ball (special 14, stype 1: weapon 720 once on each fresh press of fire, varz.c
JE_doSpecialShot; the Super Arcade's Silver Ship's second special, SASpecialWeaponB, and whatever gives it as an
item). Weapon 720 in episodes 1-3: multi 2, max 6, so the presses go round its six slots two at a time (shots.c
player_shot_create: shotMultiPos):
  press 1: slots 1 2: two balls at bx -20 by -15, both straight up the screen at 10 pixels a tick (sx 0, sy 10): two
           balls made at the same place in the same tick, flying together (two coincident models, two glows on one spot)
  press 2: slot 3 up and left (sx -8, sy 8, bx -30 by -10), slot 4 up and right (sx 8, sy 8, bx -10 by -10)
  press 3: slot 5 left (sx -10, sy 0, bx -40 by -10), slot 6 right (sx 10, sy 0, bx 0 by -10)
attack 4 (each ball dies on what it hits unless that is weaker), del 255; episodes 4-5: multi 1, max 1, slot 1 only,
attack 8. The shape's graphic is sg 60022: OPTION_SHAPES 21 (shots.c: sprite_frame - 60001), drawn with
blit_sprite_blend from its top left (hue from the shape, value the average of the screen's and the shape's: half
see-through); in 3D models.cfg's "shot options 21" line puts this model on the shape's middle (layer3d.c
l3d_add_option_shot), keyed and moving between ticks as a shot, its glow= its only glow.

As the shape draws it (ramp 4, rose red: 0x43 .. 0x4f; one hex digit a pixel below, its shade): a ball 55 x 54 (a
circle of radius 27.5 round the shape's middle, 0.1 left and 0.3 up of it), lit from the upper left (a broad highlight,
0x4f, up and left of its middle), its limb darker (0x44-0x46); over it a planet's relief drawn lit from the upper left:
pale swirling ridges (0x4b-0x4e) across its middle with dark lines under them, a crater ring up and right (0x48 round
0x46), small craters down its right side, dark pits and folds (0x44-0x46) along its bottom.

The model (shot_xega): a ball, round (not a half-body: it is 55 pixels across, and the game's camera, 20 degrees from
straight down and 35 at the top of the view, sees up to 0.57 of its radius of its near side below its middle; a
half-body's flat rim would show as a straight lower edge up to 5 pixels short of round), cut flat CUT of its radius
below its middle (nobody sees lower: a flat disc of
the darkest band closes it). Its surface carries the shape's relief and colours:
- the light taken out: the shape's shades less a fit of its lighting on the sphere (least squares: second order
  spherical harmonics of the ball's normal plus a gaussian on the highlight); what is left (the detail: ridges bright,
  their shadowed sides and pits dark) is the pattern.
- the pattern is laid on the ball leant LEAN degrees towards the camera (projected along the camera's direction, not
  straight down, so that the camera sees the ridges where the shape draws them); round the back of that projection
  (seen only at grazing angles) the rim's values, fading to plain body.
- the relief: the detail (blurred over SIGMA_H pixels, clipped) times RELIEF pixels a shade along the ball's normal,
  fading out near the pattern's rim: the pale ridges raised, the dark lines and pits sunk, the crater's ring raised
  round its sunk floor; the game's sun (also from the upper left) shades them.
- the colours: BASE plus the detail (blurred over SIGMA_A) in bands of ramp 4 (BANDS: 0x45 .. 0x4c), each glowing a
  little in its own colour (0.10-0.24: it reads over dark ground and keeps its night side red); the bands' borders cut
  into the mesh along the colour's contours (each triangle split where a border crosses it, the new points shared
  between neighbours), so that every face lies in one band and the borders run smooth, not in steps.
- the mesh: rings round the ball's top, about SPACING pixels apart along its surface (coarser below its middle),
  stitched, then refined where the relief bends (refine: an edge split where its middle's relief lies more than
  REFINE_TOL from its ends' mean, down to REFINE_MIN, twice), so that the ridges get the triangles; the normals the
  unsplit mesh's (smooth across the bands' cuts). 14 214 triangles (8 894 before the bands' cuts, 60 the cut's disc),
  8 materials. Tried: the detail blurred less for the colours (sigma 0.5-0.7): crisper swirls but 18-19k triangles
  (many small islands of colour to cut round); blurred more for the relief (0.7): the swirls lost.
- the glow (GLOW): 70 pixels at 0.3 in 0x4b round its middle: a thin rose halo, an atmosphere over dark ground
  (0.35 tried: a little strong on the first press, whose two coincident balls glow twice; 60 at 0.2: not seen).
  Each glow's light costs about 0.24 ms of GPU time (polish_shot_plasmastorm.py's docstring); one or two balls,
  briefly.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera; the origin at the
shape's middle (column c is x = c + 0.5 - 27.5, row r is y = 27 - (r + 0.5)): the game puts the model's origin there
and centres it in height on the player's layer.

models.cfg: see the block's comment (--cfg <file> appends the lines).

Run: Blender -b --factory-startup -P tools/blender/models/shots/polish_shot_xega.py -- [--outdir <dir>] (default
     assets/models/shots) [--check <any>] (the top view's silhouette against the shape's pixels above)
     [--preview <prefix>] (top, three-quarter and game-camera views) [--cfg <file>]
"""
import math
import os
import sys

import bpy
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polish_shot_fireball as kit  # noqa: E402
from polish_shot_fireball import k, mk, view  # noqa: E402

NAME = "shot_xega"
SHAPE = 21

# Option shape 21, one hex digit a pixel: its shade of ramp 4 ('.' transparent).
XEGA = """
.....................556666666665544...................
.................4566777777888777665533................
...............56778888888996666777666554..............
.............567888888888a96788877776666553............
...........5778888999999aa778888877777776654...........
..........57888999999999aa7789988878778877664..........
.........6788999999aaa99aa88899988797777889874.........
........67889999aabbccd9aa988999887a87777889974........
.......6788999aaaabbcef9aaa88899889a887766789975.......
......6788999aaaaabbdfb99aa978888ac88887767789863......
.....67889aaaabbcccdeca999aa9889bc9988877667899753.....
....57889abcbbcddeeeddca99aaabcdc999888877677888653....
...47789aabbdcdeffffeddcbcddcccbbb99988877677787664....
...5789aaabdfeeffffffeeddfecbabbbba99888776677776654...
..5689aaaabeefffffffffedfeca8889bbba9988877666676664...
..668aaaabeddeffffffffefeca889989cbaa9888776666688754..
.4669aaacedbdeffffffffffdba899999dbaaa98877666669b865..
.56679acdb9adefffffffffecba89aaa9dcbaaa9877666668b8653.
36788889999bdeffffffffedcb98aaaa9bdcbbaa97766666688654.
4568988999abceeffffffeedcb89abcca9bcccbb98766545666664.
7468899aaaabcdeeffffeedcba8aadfcba99999ab9765344566775.
8667899aaaaabcdeeeeeedcba99aacedbba98888ab7643455678754
8757799aaaaaabccddddcbba99aaaadcbbaa98888c7644555778764
8846799aaaaaaabbbbbbbba99aaaaaabbbb999888b8645765788765
8866689aaaaaaaaaaaaaaa9cfedcbbaaaaa999889a9646965788765
88677789aaaaaaaaaaa999cfdccccbbaaaa99989b97647865798765
877788889aaaaa9999999bddcbbbbbbbaa9998ab8876467657a8765
86788998889999999999bdcbbbbbbbbbaa9abba98865455558a9765
76788999cfecbbbbaaaacbbbbbbbbbbbabbba9977764587569b8765
6678899cfdaaaaaaaaabbbaaaaaabbbabda8789776547b956ab8765
667888acba9aaaaaaaabbaaaaaaaaaaada7778a7764479958bb8764
567789ba989bbbbaaaabaaaaaaaaaa9ba77779a765456868bca8664
467789a988acaaaaaaabaaaaaaaaa99a87778a976445568aeb9866.
4567789888ba9aaaaaaaaaaaaaaa999997789976445557acca9765.
.5666798778a999aaaaaaaaaa999999988888764455689b99a9764.
.566659877789999999999999999999888777654567898988b8763.
.456559887788999999999999999abbba977654467757788aa775..
..4557988877778999999999999acba766866544654578aba9774..
..467888888877788888888889aeb875557665466457abcba876...
...5777888888888888888889abb765555777645457aba9a9775...
....5778888888888888999abba8655555566764579b99a9876....
....5578885677888899abbba98765555566677556db9aa8765....
.....567864444577777888899887655566667775ae9aa9765.....
......56854555566665555557888777777778778bdab8765......
.......576555576655555555435677666667789bedb8765.......
........5765677645555665654546777677789acdb9765........
.........5777764555666665555656688789aabda8765.........
..........4666644566555556666777799aa9ba98665..........
...........44665444556666777777788a9aa997654...........
............3456676777777777788899aa9876544............
..............455777777777888999998876654..............
................44677788888887776666544................
..................3456666666666655433..................
......................44555554444......................
"""

# The ball: how far it leans its pattern towards the camera (degrees), where it is cut flat (times its radius below its
# middle), the mesh's spacing along its surface (pixels: on top, below its middle).
LEAN = 22.0
CUT = 0.65
SPACING, SPACING_BELOW = 1.3, 2.2
# The refinement: edges along which the relief bends more than REFINE_TOL pixels from straight are split, down to
# REFINE_MIN pixels long, at most REFINE_LEVELS times.
REFINE_TOL, REFINE_MIN, REFINE_LEVELS = 0.08, 0.5, 2
# The relief: the detail blurred over SIGMA_H pixels, clipped to RELIEF_CLIP (shades), times RELIEF pixels a shade,
# fading out from RELIEF_FADE[0] to RELIEF_FADE[1] of the pattern's radius.
SIGMA_H, RELIEF_CLIP, RELIEF, RELIEF_FADE = 0.5, (-3.0, 3.5), 0.4, (0.8, 0.93)
# The colours: BASE plus KA times the detail blurred over SIGMA_A, in BANDS (lowest value, palette index, emission).
SIGMA_A, BASE, KA = 1.0, 8.6, 0.8
BANDS = [(-99.0, 0x45, 0.10), (5.5, 0x46, 0.12), (6.5, 0x47, 0.14), (7.5, 0x48, 0.16), (8.5, 0x49, 0.18),
         (9.5, 0x4a, 0.20), (10.5, 0x4b, 0.22), (11.5, 0x4c, 0.24)]
ROUGHNESS = 0.5
# The glow (glow=): size, strength (each of the two coincident balls of the first press), colour, dx, dy.
GLOW = (70, 0.3, 0x4b, 0.0, 0.0)


# --- The shape and its fields -----------------------------------------------------------------------------------------

def shades():
    """The shape's pixels: shades (rows from the top), nan where transparent."""
    rows = XEGA.strip("\n").splitlines()
    return np.array([[np.nan if ch == "." else float(int(ch, 16)) for ch in r] for r in rows])


def blur(a, sigma):
    """a blurred (a Gaussian of sigma pixels) within its pixels (nan outside)."""
    mask = np.isfinite(a)
    v = np.where(mask, np.nan_to_num(a), 0.0)
    reach = int(3 * sigma) + 1
    g = np.exp(-np.arange(-reach, reach + 1) ** 2 / (2.0 * sigma * sigma))

    def b(z):
        z = np.apply_along_axis(lambda m: np.convolve(m, g, mode="same"), 0, z)
        return np.apply_along_axis(lambda m: np.convolve(m, g, mode="same"), 1, z)
    num, den = b(v), b(mask.astype(float))
    return np.where(mask, num / np.maximum(den, 1e-9), np.nan)


def filled(a):
    """a with its nan pixels given their nearest pixel's value (rings outwards), for sampling at the rim."""
    out = a.copy()
    while np.isnan(out).any():
        known = np.isfinite(out)
        grown = out.copy()
        for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)):
            shifted = np.full(out.shape, np.nan)
            src = out[max(0, -dr):out.shape[0] - max(0, dr), max(0, -dc):out.shape[1] - max(0, dc)]
            shifted[max(0, dr):out.shape[0] - max(0, -dr) if dr < 0 else out.shape[0],
                    max(0, dc):out.shape[1] - max(0, -dc) if dc < 0 else out.shape[1]] = src
            take = ~known & np.isfinite(shifted) & np.isnan(grown)
            grown[take] = shifted[take]
        out = grown
    return out


class Shape:
    """The shape's circle and its fields (the detail, the height, the colour), sampled in model coordinates."""

    def __init__(self):
        S = shades()
        self.S = S
        h, w = S.shape
        self.h, self.w = h, w
        mask = np.isfinite(S)
        self.mask = mask
        # the circle: least squares through the outline's pixel edges (rows' and columns' ends)
        edge = []
        for r in range(h):
            cs = np.where(mask[r])[0]
            if len(cs):
                edge += [(cs[0] - w / 2.0, h / 2.0 - (r + 0.5)), (cs[-1] + 1 - w / 2.0, h / 2.0 - (r + 0.5))]
        for c in range(w):
            rs = np.where(mask[:, c])[0]
            if len(rs):
                edge += [(c + 0.5 - w / 2.0, h / 2.0 - rs[0]), (c + 0.5 - w / 2.0, h / 2.0 - (rs[-1] + 1))]
        E = np.array(edge)
        A = np.c_[2 * E[:, 0], 2 * E[:, 1], np.ones(len(E))]
        (cx, cy, c0), *_ = np.linalg.lstsq(A, (E ** 2).sum(1), rcond=None)
        self.cx, self.cy = float(cx), float(cy)
        self.radius = float(math.sqrt(c0 + cx * cx + cy * cy))
        # the light: a fit on the sphere's normal (second order harmonics) and a gaussian on the highlight
        yy, xx = np.mgrid[0:h, 0:w]
        X, Y = xx + 0.5 - w / 2.0, h / 2.0 - (yy + 0.5)
        nx, ny = (X - self.cx) / self.radius, (Y - self.cy) / self.radius
        nz = np.sqrt(np.clip(1 - nx * nx - ny * ny, 0, 1))
        hot = mask & (np.nan_to_num(S) >= 14.5)
        hx, hy = X[hot].mean(), Y[hot].mean()
        gauss = np.exp(-((X - hx) ** 2 + (Y - hy) ** 2) / (2 * 6.0 ** 2))
        cols = [np.ones_like(nx), nx, ny, nz, nx * ny, nx * nz, ny * nz, nx * nx - ny * ny, 3 * nz * nz - 1, gauss]
        M = np.stack([c[mask] for c in cols], 1)
        coef, *_ = np.linalg.lstsq(M, S[mask], rcond=None)
        light = np.full(S.shape, np.nan)
        light[mask] = M @ coef
        self.detail = S - light
        self.height = filled(np.clip(blur(self.detail, SIGMA_H), *RELIEF_CLIP))
        self.colour = filled(BASE + KA * blur(self.detail, SIGMA_A))
        self.rim_colour = BASE

    def sample(self, field, x, y):
        """field (rows from the top, filled) at a point (model coordinates), bilinear, clamped to the shape's box."""
        c = min(max(x + self.w / 2.0 - 0.5, 0.0), self.w - 1.0)
        r = min(max(self.h / 2.0 - y - 0.5, 0.0), self.h - 1.0)
        c0, r0 = min(int(c), self.w - 2), min(int(r), self.h - 2)
        fc, fr = c - c0, r - r0
        return float(field[r0, c0] * (1 - fc) * (1 - fr) + field[r0, c0 + 1] * fc * (1 - fr) +
                     field[r0 + 1, c0] * (1 - fc) * fr + field[r0 + 1, c0 + 1] * fc * fr)


# --- The ball ---------------------------------------------------------------------------------------------------------

class Ball:
    """The ball: its surface point, relief and colour for a direction from its middle."""

    def __init__(self, shape):
        self.shape = shape
        self.R = shape.radius
        self.centre = (shape.cx, shape.cy, 0.0)
        lean = math.radians(LEAN)
        self.axis = (0.0, -math.sin(lean), math.cos(lean))  # (the pattern is projected along it)
        self.up = (0.0, math.cos(lean), math.sin(lean))  # (the pattern's up, across the axis)

    def pattern(self, u):
        """Where the direction u falls on the shape (model coordinates), how far out (0 the middle, 1 the rim) and how
        far round the back of the projection (0 in front, 1 well behind)."""
        px = u[0]
        py = u[0] * self.up[0] + u[1] * self.up[1] + u[2] * self.up[2]
        pz = u[0] * self.axis[0] + u[1] * self.axis[1] + u[2] * self.axis[2]
        rho = math.hypot(px, py)
        behind = 0.0
        if pz < 0.0:  # (behind the projection's rim: the rim's values, fading to plain body)
            behind = mk.smoothstep(0.0, 0.3, -pz)
            scale = 0.97 / max(rho, 1e-9)
            px, py, rho = px * scale, py * scale, 0.97
        return self.shape.cx + px * self.R, self.shape.cy + py * self.R, rho, behind

    def relief(self, u):
        x, y, rho, behind = self.pattern(u)
        if behind > 0.0:
            return 0.0
        fade = 1.0 - mk.smoothstep(RELIEF_FADE[0], RELIEF_FADE[1], rho)
        return RELIEF * self.shape.sample(self.shape.height, x, y) * fade

    def colour(self, u):
        x, y, rho, behind = self.pattern(u)
        value = self.shape.sample(self.shape.colour, x, y)
        return value * (1.0 - behind) + self.shape.rim_colour * behind

    def point(self, u):
        r = self.R + self.relief(u)
        return (self.centre[0] + r * u[0], self.centre[1] + r * u[1], self.centre[2] + r * u[2])


def ring_thetas(R):
    """The rings' angles from the top (radians) down to the cut, about SPACING pixels apart on top and SPACING_BELOW
    below the middle (blending between 80 and 100 degrees)."""
    end = math.acos(-CUT)
    thetas = [0.0]
    while thetas[-1] < end:
        t = thetas[-1]
        f = mk.smoothstep(math.radians(80.0), math.radians(100.0), t)
        thetas.append(t + (SPACING * (1 - f) + SPACING_BELOW * f) / R)
    scale = end / thetas[-1]
    return [t * scale for t in thetas]


def build_ball_mesh(ball):
    """The ball's surface: (vertices, triangles, values (the colour at each vertex), normals) and the cut's disc:
    (vertices, triangles). Rings of directions, stitched, then refined where the relief bends (refine)."""
    R = ball.R
    thetas = ring_thetas(R)
    dirs, rings = [], []
    for i, t in enumerate(thetas):
        if i == 0:
            n, phase = 1, 0.0
        else:
            f = mk.smoothstep(math.radians(80.0), math.radians(100.0), t)
            n = max(6, int(round(2 * math.pi * R * math.sin(t) / (SPACING * (1 - f) + SPACING_BELOW * f))))
            phase = 0.5 * (i % 2)
        start = len(dirs)
        for j in range(n):
            phi = 2 * math.pi * (j + phase) / n
            dirs.append((math.sin(t) * math.cos(phi), math.sin(t) * math.sin(phi), math.cos(t)))
        rings.append((start, n, phase))
    tris = []
    s0 = rings[1]
    for j in range(s0[1]):  # (the fan round the top)
        tris.append((0, s0[0] + j, s0[0] + (j + 1) % s0[1]))
    for (a0, na, pa), (b0, nb, pb) in zip(rings[1:-1], rings[2:]):
        i = j = 0
        while i < na or j < nb:
            ai = 2 * math.pi * (i + 1 + pa) / na
            bj = 2 * math.pi * (j + 1 + pb) / nb
            if j >= nb or (i < na and ai <= bj):
                tris.append((a0 + i % na, b0 + j % nb, a0 + (i + 1) % na))
                i += 1
            else:
                tris.append((a0 + i % na, b0 + j % nb, b0 + (j + 1) % nb))
                j += 1
    last0, nl, _ = rings[-1]
    rim = set(range(last0, last0 + nl))
    dirs, tris = refine(ball, dirs, tris, rim)
    verts = [ball.point(u) for u in dirs]
    values = [ball.colour(u) for u in dirs]
    normals = vertex_normals(verts, tris)
    disc = [verts[last0 + j] for j in range(nl)] + [(ball.centre[0], ball.centre[1], -CUT * R)]
    disc_tris = [(nl, (j + 1) % nl, j) for j in range(nl)]
    return (verts, tris, values, normals), (disc, disc_tris)


def refine(ball, dirs, tris, keep):
    """Splits the edges along which the relief bends more than REFINE_TOL pixels from straight (its middle's relief
    against its ends' mean), down to REFINE_MIN pixels, REFINE_LEVELS times; each triangle split by how many of its
    edges are (1: in two, 2: in three, 3: in four), so that no point lies on another triangle's edge. Edges between two
    points of keep (the cut's rim) are never split."""
    dirs = list(dirs)
    relief = [ball.relief(u) for u in dirs]

    def unit(a, b):
        m = [a[i] + b[i] for i in range(3)]
        length = math.sqrt(sum(c * c for c in m))
        return tuple(c / length for c in m)
    for _ in range(REFINE_LEVELS):
        mids = {}
        for tri in tris:
            for e in ((tri[0], tri[1]), (tri[1], tri[2]), (tri[2], tri[0])):
                key = (min(e), max(e))
                if key in mids or (key[0] in keep and key[1] in keep):
                    continue
                a, b = dirs[key[0]], dirs[key[1]]
                length = ball.R * math.acos(min(1.0, sum(a[i] * b[i] for i in range(3))))
                if length < REFINE_MIN:
                    continue
                m = unit(a, b)
                r = ball.relief(m)
                if abs(r - (relief[key[0]] + relief[key[1]]) / 2) > REFINE_TOL:
                    dirs.append(m)
                    relief.append(r)
                    mids[key] = len(dirs) - 1
        out = []
        for a, b, c in tris:
            mab, mbc, mca = (mids.get((min(a, b), max(a, b))), mids.get((min(b, c), max(b, c))),
                             mids.get((min(c, a), max(c, a))))
            n = sum(m is not None for m in (mab, mbc, mca))
            if n == 0:
                out.append((a, b, c))
            elif n == 3:
                out += [(a, mab, mca), (mab, b, mbc), (mca, mbc, c), (mab, mbc, mca)]
            else:
                # rotate so that the split edges come first: (a b) split, then maybe (b c)
                for _ in range(3):
                    if mids.get((min(a, b), max(a, b))) is not None and (
                            n == 1 or mids.get((min(b, c), max(b, c))) is not None):
                        break
                    a, b, c = b, c, a
                mab = mids[(min(a, b), max(a, b))]
                if n == 1:
                    out += [(a, mab, c), (mab, b, c)]
                else:
                    mbc = mids[(min(b, c), max(b, c))]
                    out += [(a, mab, c), (mab, b, mbc), (mab, mbc, c)]
        tris = out
    return dirs, tris


def vertex_normals(verts, tris):
    V = np.array(verts)
    T = np.array(tris)
    fn = np.cross(V[T[:, 1]] - V[T[:, 0]], V[T[:, 2]] - V[T[:, 0]])  # (area-weighted)
    n = np.zeros_like(V)
    for c in range(3):
        np.add.at(n, T[:, c], fn)
    return [tuple(v / max(np.linalg.norm(v), 1e-12)) for v in n]


def split_bands(verts, tris, values, normals, thresholds):
    """Cuts every triangle along each threshold's contour of the values (linear over each triangle; the points where a
    contour crosses an edge shared between neighbours): every resulting triangle lies within one band. Returns new
    (verts, tris, values, normals)."""
    verts, values, normals = list(verts), list(values), list(normals)
    eps = 1e-9
    for t in thresholds:
        cache = {}

        def cross(a, b):
            key = (min(a, b), max(a, b))
            if key not in cache:
                fa, fb = values[a], values[b]
                s = (t - fa) / (fb - fa)
                pa, pb = verts[a], verts[b]
                verts.append(tuple(pa[i] + (pb[i] - pa[i]) * s for i in range(3)))
                na, nb = normals[a], normals[b]
                n = [na[i] + (nb[i] - na[i]) * s for i in range(3)]
                length = math.sqrt(sum(c * c for c in n)) or 1.0
                normals.append(tuple(c / length for c in n))
                values.append(t)
                cache[key] = len(verts) - 1
            return cache[key]

        out = []
        for tri in tris:
            side = [1 if values[v] > t + eps else -1 if values[v] < t - eps else 0 for v in tri]
            if not (1 in side and -1 in side):
                out.append(tri)
                continue
            # rotate so that the lone vertex (alone on its side, or the one on the contour) comes first
            for r in range(3):
                a, b, c = tri[r], tri[(r + 1) % 3], tri[(r + 2) % 3]
                sa, sb, sc = side[r], side[(r + 1) % 3], side[(r + 2) % 3]
                if sa == 0:  # (on the contour; b and c on opposite sides)
                    m = cross(b, c)
                    out += [(a, b, m), (a, m, c)]
                    break
                if sb == sc and sb != sa and 0 not in (sb, sc):  # (a alone)
                    mab, mac = cross(a, b), cross(a, c)
                    out += [(a, mab, mac), (mab, b, c), (mab, c, mac)]
                    break
                if 0 in (sb, sc) and sa != 0 and 0 not in (sa,):
                    # (one of b, c on the contour, the other opposite a)
                    if sb == 0 and sc == -sa:
                        m = cross(a, c)
                        out += [(a, b, m), (b, c, m)]
                        break
                    if sc == 0 and sb == -sa:
                        m = cross(a, b)
                        out += [(a, m, c), (m, b, c)]
                        break
            else:
                raise ValueError("unsplit triangle %s %s" % (tri, side))
        tris = out
    return verts, tris, values, normals


def band_of(value):
    return max(i for i, b in enumerate(BANDS) if value >= b[0])


def build_model():
    shape = Shape()
    ball = Ball(shape)
    (verts, tris, values, normals), (disc, disc_tris) = build_ball_mesh(ball)
    before = len(tris)
    verts, tris, values, normals = split_bands(verts, tris, values, normals, [b[0] for b in BANDS[1:]])
    mats = kit.materials("xega", BANDS, roughness=ROUGHNESS)
    body = k.mesh_object(NAME + "_body", verts, tris)
    for m in mats:
        body.data.materials.append(m)
    for poly in body.data.polygons:
        poly.material_index = band_of(sum(values[v] for v in poly.vertices) / 3.0)
        poly.use_smooth = True
    body.data.normals_split_custom_set_from_vertices(normals)
    base = k.mesh_object(NAME + "_cut", disc, disc_tris)
    base.data.materials.append(mats[0])
    print("ball: circle %.2f %.2f radius %.2f; %d triangles before the bands' cuts, %d after; cut disc %d" % (
        shape.cx, shape.cy, shape.radius, before, len(tris), len(disc_tris)))
    return [body, base], shape


def cfg_lines():
    size, strength, colour, dx, dy = GLOW
    return (["model %s shots/%s.glb" % (NAME, NAME)],
            ["shot options %d %s glow=%d:%.2f:%d:%g:%g  # the Xega Ball" % (SHAPE, NAME, size, strength, colour,
                                                                            dx, dy)])


def build():
    options = k.args()
    outdir = options.get("outdir", kit.OUTDIR)
    k.reset()
    parts, shape = build_model()
    bpy.context.view_layer.update()
    print("== %s (option shape %d): the Xega Ball" % (NAME, SHAPE))
    if "check" in options:
        mask = [[bool(np.isfinite(v)) for v in row] for row in shape.S]
        mk.compare("%s (option shape %d)" % (NAME, SHAPE), mk.coverage(parts, shape.w, shape.h), mask)
    if "cfg" in options:
        models, shots = cfg_lines()
        with open(options["cfg"], "a") as out:
            out.write("\n".join(models + shots) + "\n")
    bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
    mk.report(NAME, parts, os.path.join(outdir, NAME + ".glb"))
    if "preview" in options:
        view(options["preview"] + NAME, parts, size=(shape.w, shape.h))


if __name__ == "__main__":
    build()
