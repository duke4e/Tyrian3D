"""The front weapon pick-ups of the power-ups sheet ("twoplayer" in the catalogue; values 30001-30031, the weapon
port they give; 2x2 sprites, 24 x 28 pixels, one frame each; dropped by enemies in every episode, a few placed on
the ground), polished (2026-10-21; they replace powerups_front.py's models): an ice-blue orb with the weapon's symbol
on its face. models.cfg: model pu_<name> items/pu_<name>.glb and sprite powerups <n> pu_<name> yaw=0, unchanged
(no spin: the symbols stay upright as the sprites draw them, and the orb is painted for the camera, see below).

- pu_pulse_cannon (153): a light P on a red badge, an amber flame in its crest (Pulse-Cannon)
- pu_multi_cannon (155): a light M on a red winged badge, amber flames in its crest and wings (Multi-Cannon)
- pu_mega_cannon (157): a fireball dripping three tongues of fire (Mega Cannon)
- pu_laser (159): a rod of light, white-hot along its middle (Laser)
- pu_zica_laser (161): a blue crystal drop with a glowing heart (Zica Laser)
- pu_protron (163): three pale pearls in a dark socket (Protron)
- pu_vulcan (165): three bullets flying up, staggered, their noses hot (Vulcan Cannon)
- pu_lightning (167): a bolt of blue plasma with a white-hot streak down it (Lightning Cannon)
- pu_missile (201): a light grey rocket with a dark seeker slot in its nose and swept fins (Missile Launcher)
- pu_heavy_missile (203): a green rocket with a gold band and brown fins (Heavy Missile Launcher)
- pu_guided_bombs (267): a steel bomb with a four-pointed star and a red seeker eye (Guided Bombs)
- pu_hyper_pulse (269): a light H on a red badge pointing up, an amber flame in its point (Hyper Pulse)

None of the twelve is another sprite's pixels mirrored, turned or in other ramps (157's outline is the sidekick
Charge Cannon's, 229, in other colours: its FIRE shape can serve that one). No other enemy shows these sprites.

The orb. Every orb sprite of the sheet draws one ball shade for shade, in ramp 13 (ice blue: these), 4 (flesh red:
the rear weapons) or 2 (green: the sidekicks): columns 2-21, rows 3-23 (round (0, 0.5), 10 across and 10.5 up either
way), a cross of darker grooves (column 11, row 13), its upper left lighter where the sun lights it and its lower
right lighter again where the light through it gathers (the sprite's lighter pixels at columns 15-18, rows 16-20), a
darker outline. orb(ramp) builds it in any ramp, for the rear weapons' and the sidekicks' rounds too: a glossy ball of
glazed ice (palette shade 8, glowing faintly in shade 9, so that its side away from the sun stays ice blue from the
slanted camera rather than going near black), its rim darker in two bands (shades 7 and 5: the sprite's outline), the
cross sunk in as round grooves with soft shoulders (shade 2 in their bottoms), and the gathered light a crescent of
lighter glowing ice inside the rim's lower right (shades 11 and 13). The sprite's fainter lighter lines beside the
cross are left to the sun's glint and the crescent (painted as lines they read as a grid of window bars).

Painted for the camera. The game's camera looks 20 degrees from straight down, from the bottom of the screen
(VIEW_TILT). The models are built in view space, where the camera looks straight down and the sprite is the top view,
and to_world() tilts them into the game's axes about the ball's middle: the cross shows as straight lines through the
middle as the sprite draws it, the crescent sits in the lower right, and every symbol shows exactly where the sprite
draws it (from straight above it sits about 3 pixels lower on the ball; the top-view overlaps are listed too).

The symbols are reliefs (relief()): a shape, a 2D signed distance field over the sprite's pixels (circles, boxes,
polygons, strokes, joined, cut and rounded), raised over a dome a little flatter than the ball (DOME_R), its edge a
quarter round or any profile (a rod's, a pearl's, a cabochon's), its wall straight down into the ball; built from the
outline's rings at the profile's depths (exact offsets of the outline), its normals the shape's own (from the
outline's distance and the profile), painted in bands by depth (fire, light, crystal, bullets) or by fields (a
letter darker downwards, a drop's heart, a bolt's streak). Each symbol sits on a dark setting in the sprite's outline
colour (its dark outline pixels), hollow where the symbol covers it. The rockets are lathed and bent with the dome.
Glowing parts glow 0.2-0.6 (the game's bloom adds), in their own palette colours; at most 14 materials per model.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera; origin at the
sprite's centre (pixel 12, 14); column c is x = c + 0.5 - 12, row r is y = 13.5 - r. The game centres the models in
height on their layer.

Replaces powerups_front.py (all of it: ICON_153/155/269/161/167 and the twelve builders, MODELS) and the parts of
powerups_parts.py only it used: badge(), ribbon_from_rows() (and rows_of() and body_from_rows(), which only they
read, and RAMP_ICE); powerups.py's import of powerups_front and its place in the MODELS loop.

Later rounds (rear weapons, sidekicks): import polish_powerups_front (no side effects; build() runs only as a
script): orb(4) or orb(2) for the red and green orbs, relief(), paint(), the shape fields, then to_world(parts) and
triangulate(parts) before kit.report().

Options after "--": --outdir <dir> (default assets/models/items), --check <sheets dir or powerups.png> (each model's
silhouette as the game's camera sees it and from straight above against its sprite), --preview <prefix> (top and
3/4 views), --only <name,...>.
"""
import math
import os
import sys

import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polish_item_kit as kit  # noqa: E402
from polish_item_kit import k  # noqa: E402

SHEET = "powerups.png"
VIEW_TILT = 20.0
T = math.radians(VIEW_TILT)

# --- 2D shapes: signed distance fields over the sprite (inside < 0), in pixels ---------------------------------------
# x = c + 0.5 - 12, y = 13.5 - r for column c and row r of the 2x2 sprite.

STEP = 0.08
GRID_X = np.arange(-13.0, 13.0 + 1e-9, STEP)
GRID_Y = np.arange(-15.0, 15.0 + 1e-9, STEP)


def px(col):
    return col + 0.5 - 12


def py(row):
    return 13.5 - row


def circle(cx, cy, r):
    return lambda x, y: np.hypot(x - cx, y - cy) - r


def ellipse(cx, cy, a, b):
    """An ellipse (its field is a distance near the outline only)."""
    m = min(a, b)
    return lambda x, y: (np.hypot((x - cx) / a, (y - cy) / b) - 1.0) * m


def box(x0, x1, y0, y1, r=0.0):
    """A rectangle with corners rounded by r."""
    cx, cy, hw, hh = (x0 + x1) / 2, (y0 + y1) / 2, (x1 - x0) / 2, (y1 - y0) / 2

    def f(x, y):
        qx = np.abs(x - cx) - hw + r
        qy = np.abs(y - cy) - hh + r
        return np.hypot(np.maximum(qx, 0.0), np.maximum(qy, 0.0)) + np.minimum(np.maximum(qx, qy), 0.0) - r
    return f


def polygon(points):
    """A polygon [(x, y), ...] (either winding; repeated points are dropped)."""
    kept = []
    for p in points:
        if not kept or math.hypot(p[0] - kept[-1][0], p[1] - kept[-1][1]) > 1e-6:
            kept.append(p)
    if len(kept) > 1 and math.hypot(kept[0][0] - kept[-1][0], kept[0][1] - kept[-1][1]) <= 1e-6:
        kept.pop()
    pts = np.asarray(kept, float)

    def f(x, y):
        x = np.asarray(x, float)
        y = np.asarray(y, float)
        d = np.full(np.broadcast(x, y).shape, np.inf)
        s = np.ones(d.shape)
        n = len(pts)
        for i in range(n):
            ax, ay = pts[i]
            bx, by = pts[(i + 1) % n]
            ex, ey = bx - ax, by - ay
            wx, wy = x - ax, y - ay
            t = np.clip((wx * ex + wy * ey) / (ex * ex + ey * ey), 0.0, 1.0)
            dx, dy = wx - ex * t, wy - ey * t
            d = np.minimum(d, dx * dx + dy * dy)
            c1, c2, c3 = y >= ay, y < by, ex * wy > ey * wx
            s = np.where((c1 & c2 & c3) | (~c1 & ~c2 & ~c3), -s, s)
        return s * np.sqrt(d)
    return f


def capsule(ax, ay, bx, by, r):
    """A stroke from (ax, ay) to (bx, by), r wide either side, round at its ends."""
    def f(x, y):
        ex, ey = bx - ax, by - ay
        wx, wy = x - ax, y - ay
        t = np.clip((wx * ex + wy * ey) / (ex * ex + ey * ey), 0.0, 1.0)
        return np.hypot(wx - ex * t, wy - ey * t) - r
    return f


def union(*fields):
    return lambda x, y: np.minimum.reduce([f(x, y) for f in fields])


def intersect(*fields):
    return lambda x, y: np.maximum.reduce([f(x, y) for f in fields])


def minus(a, *others):
    return lambda x, y: np.maximum.reduce([a(x, y)] + [-b(x, y) for b in others])


def grow(f, d):
    return lambda x, y: f(x, y) - d


def blend(a, b, r):
    """a and b joined with a fillet of radius r where they meet (a smooth union)."""
    def f(x, y):
        da, db = a(x, y), b(x, y)
        h = np.clip(0.5 + 0.5 * (db - da) / r, 0.0, 1.0)
        return db * (1 - h) + da * h - r * h * (1 - h)
    return f


def mirrored(f):
    return lambda x, y: f(-np.asarray(x), y)


def symmetric(f):
    """f and its mirror image across x = 0."""
    return union(f, mirrored(f))


# --- Contours ----------------------------------------------------------------------------------------------------

def _window(field, pad=1.0):
    """The grid's nodes, cut down to where the field reaches below pad (and a margin)."""
    xs, ys = GRID_X, GRID_Y
    v = field(*np.meshgrid(xs, ys))
    rows = np.nonzero((v < pad).any(axis=1))[0]
    cols = np.nonzero((v < pad).any(axis=0))[0]
    if len(rows) == 0:
        return None
    r0, r1 = max(0, rows[0] - 3), min(len(ys), rows[-1] + 4)
    c0, c1 = max(0, cols[0] - 3), min(len(xs), cols[-1] + 4)
    return xs[c0:c1], ys[r0:r1], v[r0:r1, c0:c1]


def _area(loop):
    a = 0.0
    for i in range(len(loop)):
        (x0, y0), (x1, y1) = loop[i], loop[(i + 1) % len(loop)]
        a += x0 * y1 - x1 * y0
    return a / 2


def _inside(p, loop):
    x, y = p
    inside = False
    for i in range(len(loop)):
        (ax, ay), (bx, by) = loop[i], loop[(i + 1) % len(loop)]
        if (ay > y) != (by > y) and x < ax + (y - ay) * (bx - ax) / (by - ay):
            inside = not inside
    return inside


def _simplify(points, tolerance):
    """Douglas-Peucker on an open polyline."""
    if len(points) < 3:
        return list(points)
    pts = np.asarray(points)
    keep = np.zeros(len(pts), bool)
    keep[0] = keep[-1] = True
    stack = [(0, len(pts) - 1)]
    while stack:
        i, j = stack.pop()
        if j <= i + 1:
            continue
        a, b = pts[i], pts[j]
        e = b - a
        length = math.hypot(*e)
        seg = pts[i + 1:j] - a
        if length > 1e-9:
            d = np.abs(e[0] * seg[:, 1] - e[1] * seg[:, 0]) / length
        else:
            d = np.hypot(seg[:, 0], seg[:, 1])
        m = int(np.argmax(d))
        if d[m] > tolerance:
            keep[i + 1 + m] = True
            stack += [(i, i + 1 + m), (i + 1 + m, j)]
    return [tuple(p) for p in pts[keep]]


def _resample(loop, spacing):
    """A closed loop with its points at most spacing apart (long straight runs split)."""
    out = []
    for i in range(len(loop)):
        a, b = loop[i], loop[(i + 1) % len(loop)]
        n = max(1, int(math.ceil(math.hypot(b[0] - a[0], b[1] - a[1]) / spacing)))
        for s in range(n):
            out.append((a[0] + (b[0] - a[0]) * s / n, a[1] + (b[1] - a[1]) * s / n))
    return out


def contours(field, level=0.0, tolerance=0.02, spacing=0.8, min_area=0.02):
    """The loops where the field crosses level (marching squares with linear interpolation, the saddles decided by
    the cell's middle), simplified: [(loop, is_hole)], outer loops counter-clockwise, holes clockwise."""
    w = _window(lambda x, y: field(x, y) - level)
    if w is None:
        return []
    xs, ys, v = w
    v = v.copy()
    v[0, :] = v[-1, :] = 1.0
    v[:, 0] = v[:, -1] = 1.0
    v = np.where(np.abs(v) < 1e-9, 1e-9, v)
    inside = v < 0
    case = inside[:-1, :-1] * 1 + inside[:-1, 1:] * 2 + inside[1:, 1:] * 4 + inside[1:, :-1] * 8
    cells = np.argwhere((case != 0) & (case != 15))

    def point(key):
        kind, i, j = key
        if kind == "h":  # between nodes (i, j) and (i, j + 1)
            a, b = v[i, j], v[i, j + 1]
            t = a / (a - b)
            return (xs[j] + (xs[j + 1] - xs[j]) * t, ys[i])
        a, b = v[i, j], v[i + 1, j]
        t = a / (a - b)
        return (xs[j], ys[i] + (ys[i + 1] - ys[i]) * t)

    links = {}

    def link(a, b):
        links.setdefault(a, []).append(b)
        links.setdefault(b, []).append(a)

    for i, j in cells:
        c = case[i, j]
        bottom, right, top, left = ("h", i, j), ("v", i, j + 1), ("h", i + 1, j), ("v", i, j)
        if c in (5, 10):
            centre = (v[i, j] + v[i, j + 1] + v[i + 1, j + 1] + v[i + 1, j]) / 4 < 0
            if (c == 5) == centre:  # the outside corners cut off: br and tl
                link(bottom, right)
                link(left, top)
            else:  # the inside corners cut off: bl and tr
                link(left, bottom)
                link(right, top)
            continue
        bl, br, tr, tl = c & 1, (c >> 1) & 1, (c >> 2) & 1, (c >> 3) & 1
        edges = []
        if bl != br:
            edges.append(bottom)
        if br != tr:
            edges.append(right)
        if tl != tr:
            edges.append(top)
        if bl != tl:
            edges.append(left)
        link(edges[0], edges[1])
    loops, seen = [], set()
    for start in sorted(links):
        if start in seen:
            continue
        loop, previous, current = [start], None, start
        seen.add(start)
        while True:
            options = [n for n in links[current] if n != previous and (n not in seen or n == start)]
            if not options:
                break
            nxt = options[0]
            if nxt == start:
                break
            seen.add(nxt)
            loop.append(nxt)
            previous, current = current, nxt
        if len(loop) >= 3:
            loops.append([point(key) for key in loop])
    out = []
    for loop in loops:
        far = max(range(len(loop)), key=lambda q: (loop[q][0] - loop[0][0]) ** 2 + (loop[q][1] - loop[0][1]) ** 2)
        simple = _simplify(loop[:far + 1], tolerance)[:-1] + _simplify(loop[far:] + [loop[0]], tolerance)[:-1]
        simple = _resample(simple, spacing)
        if abs(_area(simple)) >= min_area:
            out.append(simple)
    result = []
    for i, loop in enumerate(out):
        depth = sum(1 for j, other in enumerate(out) if j != i and _inside(loop[0], other))
        hole = depth % 2 == 1
        if (_area(loop) < 0) != hole:
            loop = loop[::-1]
        result.append((loop, hole))
    return result


def outline_field(loops):
    """The exact signed distance to loops ([(loop, is_hole)]; inside < 0): rings offset from it are true offsets
    (rounded where the outline turns away)."""
    segs = []
    for loop, _ in loops:
        for i in range(len(loop)):
            segs.append((loop[i], loop[(i + 1) % len(loop)]))
    A = np.array([s[0] for s in segs], float)
    B = np.array([s[1] for s in segs], float)

    def f(x, y):
        x = np.asarray(x, float)
        y = np.asarray(y, float)
        shape = np.broadcast(x, y).shape
        px_, py_ = np.broadcast_to(x, shape).ravel(), np.broadcast_to(y, shape).ravel()
        d2 = np.full(px_.shape, np.inf)
        crossings = np.zeros(px_.shape, bool)
        for start in range(0, len(A), 64):
            a, b = A[start:start + 64], B[start:start + 64]
            e = b - a
            wx = px_[:, None] - a[None, :, 0]
            wy = py_[:, None] - a[None, :, 1]
            ee = np.maximum((e * e).sum(axis=1), 1e-12)
            t = np.clip((wx * e[None, :, 0] + wy * e[None, :, 1]) / ee[None, :], 0.0, 1.0)
            dx, dy = wx - e[None, :, 0] * t, wy - e[None, :, 1] * t
            d2 = np.minimum(d2, (dx * dx + dy * dy).min(axis=1))
            ay, by = a[None, :, 1], b[None, :, 1]
            straddle = (ay > py_[:, None]) != (by > py_[:, None])
            with np.errstate(divide="ignore", invalid="ignore"):
                xc = a[None, :, 0] + (py_[:, None] - ay) * e[None, :, 0] / np.where(by - ay == 0, 1e-12, by - ay)
            crossings ^= (np.count_nonzero(straddle & (px_[:, None] < xc), axis=1) % 2).astype(bool)
        d = np.sqrt(d2)
        return np.where(crossings, -d, d).reshape(shape)
    return f


# --- The orb ---------------------------------------------------------------------------------------------------------
# Built in view space: as the game's camera sees it (20 degrees from straight down, from the bottom of the screen),
# so that its top view is the sprite; to_world() tilts it into the game's axes.

ORB_C = Vector((0.0, 0.5, 0.0))       # the middle of the ball (the sprite's: columns 2-21, rows 3-23)
ORB_R = (10.05, 10.5, 10.3)           # its radii across, up the view and towards the camera


def orb_surface(x, y):
    """The height (towards the camera) of the ball's front at view (x, y); 0 beyond its outline."""
    u, v = (x - ORB_C.x) / ORB_R[0], (y - ORB_C.y) / ORB_R[1]
    return ORB_R[2] * math.sqrt(max(0.0, 1.0 - u * u - v * v))


def to_world(objects):
    """Tilts objects built in view space into the game's axes (about the ball's middle)."""
    m = Matrix.Translation(ORB_C) @ Matrix.Rotation(T, 4, "X") @ Matrix.Translation(-ORB_C)
    for obj in objects:
        obj.data.transform(m)
        obj.data.update()


# The ball's surface: a cross of grooves (the sprite's darker column 11 and row 13: planes through the view axis, so
# that they show as straight lines), each (0 a plane x = c, 1 a plane y = c; c): GROOVE_HALF wide either side,
# GROOVE_DEPTH deep in its middle, with rounded shoulders; the mesh is cut along GROOVE_CUTS (parts of the half
# width) for its profile.
GROOVES = ((0, -0.5), (1, 0.5))
GROOVE_HALF, GROOVE_DEPTH = 0.8, 0.62
GROOVE_CUTS = (-1.0, -0.5, 0.0, 0.5, 1.0)
# The mesh: rings round the view's vertical axis every LATITUDE_STEP degrees (and on the horizontal groove's
# profile), points round them every FRONT_STEP degrees on the side the camera sees, BACK_STEP behind.
LATITUDE_STEP, FRONT_STEP, BACK_STEP = 9.0, 7.5, 45.0
# How the ball is painted, as the camera sees it (u, v: its view across and up, -1..1 over its outline; rho their
# length; angle: degrees round its middle, 0 to the right, counter-clockwise): the rim (rho over RIM: the sprite's
# outline), the outer band (rho over OUTER), the body, and the light through the ice gathering inside the lower
# right of the rim (the sprite's lighter pixels at columns 15-18, rows 16-20): crescents along the inside of the rim,
# each (part, width at its middle, half its span in degrees), round CAUSTIC_MIDDLE degrees, the brighter inside the
# wider.
RIM, OUTER = 0.905, 0.78
CAUSTIC_MIDDLE = -45.0
CAUSTIC = [("caustic", 0.25, 62.0), ("caustic_core", 0.15, 42.0)]
# (palette shade, the shade of its glow, the glow's strength, metallic, roughness) of each part of the ball.
ORB_FINISH = {
    "body": (8, 9, 0.18, 0.15, 0.24),
    "outer": (7, 8, 0.15, 0.15, 0.24),
    "rim": (5, 6, 0.12, 0.2, 0.26),
    "groove": (2, 4, 0.08, 0.1, 0.45),
    "caustic": (11, 12, 0.24, 0.1, 0.2),
    "caustic_core": (13, 14, 0.32, 0.1, 0.2),
}


def orb_materials(ramp, finish=None):
    pal = k.level_palette()
    mats = {}
    for key, (shade, glow, strength, metallic, roughness) in dict(ORB_FINISH, **(finish or {})).items():
        mats[key] = k.material(f"orb{ramp}_{key}", palette=16 * ramp + shade, metallic=metallic, roughness=roughness,
                               emission=pal[16 * ramp + glow], emission_strength=strength)
    return mats


def _profile(t):
    """A groove's depth across it (t: the distance from its middle over its half width): round, its shoulders
    meeting the ball's surface smoothly."""
    return (1.0 - t * t) ** 2 if t < 1.0 else 0.0


def _steps(lo, hi, step):
    n = max(1, int(round((hi - lo) / step)))
    return [lo + (hi - lo) * i / n for i in range(n + 1)]


def _view(p):
    """A point's place in the ball's view: (u, v, rho, angle)."""
    u, v = (p.x - ORB_C.x) / ORB_R[0], (p.y - ORB_C.y) / ORB_R[1]
    return u, v, math.hypot(u, v), math.degrees(math.atan2(v, u))


def _groove_t(p):
    """How far p is from the nearest groove's middle, over the groove's half width."""
    return min(abs((p.x if axis == 0 else p.y) - c) / GROOVE_HALF for axis, c in GROOVES)


def _crescent(p, width, span):
    """Over 0 inside a crescent along the inside of the rim, width wide at its middle, tapering to its ends span
    degrees either way of CAUSTIC_MIDDLE."""
    _, _, rho, angle = _view(p)
    a = ((angle - CAUSTIC_MIDDLE + 180.0) % 360.0 - 180.0) / span
    return rho - RIM + width * max(0.0, 1.0 - a * a) if p.z > 0.5 else -1.0


def orb(ramp, name="orb", finish=None):
    """The power-ups' orb in a palette ramp (13 ice blue: the front weapons; 4 red: the rear weapons; 2 green: the
    sidekicks), built in view space: a glossy ball of glazed ice with its cross of grooves, a dark rim and the light
    gathering inside its lower right. finish: {part: (shade, glow shade, strength, metallic,
    roughness)} to change. Returns the object."""
    mats = orb_materials(ramp, finish)
    keys = list(mats)
    rx, ry, rz = ORB_R
    # Rings round the view's vertical axis (latitudes, from the bottom up), with the horizontal groove's profile.
    lats = set(round(a, 4) for a in _steps(-90.0, 90.0, LATITUDE_STEP))
    for axis, c in GROOVES:
        if axis == 1:
            for o in GROOVE_CUTS:
                lats.add(round(math.degrees(math.asin((c + o * GROOVE_HALF - ORB_C.y) / ry)), 4))
    lats = sorted(lats)
    # Points round each ring (psi: degrees from the view axis towards +x).
    psis = _steps(-90.0, 90.0, FRONT_STEP)[:-1] + _steps(90.0, 270.0, BACK_STEP)[:-1]
    bm = bmesh.new()
    rings = []
    for lat in lats:
        a = math.radians(lat)
        y, c = ORB_C.y + ry * math.sin(a), math.cos(a)
        if abs(c) < 1e-6:
            rings.append([bm.verts.new((ORB_C.x, y, 0.0))])
            continue
        rings.append([bm.verts.new((ORB_C.x + rx * c * math.sin(math.radians(q)), y, rz * c * math.cos(math.radians(q))))
                      for q in psis])
    n = len(psis)
    for a, b in zip(rings, rings[1:]):
        for j in range(n):
            if len(a) == 1:
                bm.faces.new((a[0], b[(j + 1) % n], b[j]))
            elif len(b) == 1:
                bm.faces.new((a[j], a[(j + 1) % n], b[0]))
            else:
                bm.faces.new((a[j], a[(j + 1) % n], b[(j + 1) % n], b[j]))
    # The vertical groove's profile: cut along it (on the side the camera sees: behind, the groove is left out).
    for axis, c in GROOVES:
        if axis == 0:
            for o in GROOVE_CUTS:
                front = [f for f in bm.faces if f.calc_center_median().z > -1.0]
                geom = list({v for f in front for v in f.verts}) + list({e for f in front for e in f.edges}) + front
                bmesh.ops.bisect_plane(bm, geom=geom, plane_co=(c + o * GROOVE_HALF, 0.0, 0.0),
                                       plane_no=(1.0, 0.0, 0.0))
    # The painted parts' borders, on the side the camera sees: the rim's and the outer band's circles, the
    # crescents.
    for t in (RIM, OUTER):
        kit.split_along(bm, {v: (_view(v.co)[2] if v.co.z > -0.5 else -1.0) for v in bm.verts}, t)
    for _, width, span in CAUSTIC:
        kit.split_along(bm, {v: _crescent(v.co, width, span) for v in bm.verts}, 0.0)
    bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 4])
    # The grooves sunk in (the vertical one on the side the camera sees).
    for v in bm.verts:
        rel = v.co - ORB_C
        t = _groove_t(v.co) if v.co.z > -1.0 else abs(v.co.y - GROOVES[1][1]) / GROOVE_HALF
        if rel.length > 1e-6 and t < 1.0:
            v.co = ORB_C + rel * (1.0 - GROOVE_DEPTH * _profile(t) / rel.length)
    for f in bm.faces:
        p = f.calc_center_median()
        _, _, rho, angle = _view(p)
        if (_groove_t(p) if p.z > -1.0 else abs(p.y - GROOVES[1][1]) / GROOVE_HALF) < 0.4:
            key = "groove"
        elif p.z < 0 or rho > RIM:
            key = "rim"
        elif _crescent(p, CAUSTIC[1][1], CAUSTIC[1][2]) > 0:
            key = "caustic_core"
        elif _crescent(p, CAUSTIC[0][1], CAUSTIC[0][2]) > 0:
            key = "caustic"
        else:
            key = "outer" if rho > OUTER else "body"
        f.material_index = keys.index(key)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    obj = kit.from_bmesh(name, bm)
    for key in keys:
        obj.data.materials.append(mats[key])
    k.smooth(obj, 60.0)
    kit.drop_unused_materials(obj)
    return obj


# --- Symbols: reliefs on the ball's face -------------------------------------------------------------------------
# A relief is a shape (a 2D field) raised over the ball's face as the camera sees it: its top TOP over a gentle dome
# (DOME_R: the dome's radius, flatter than the ball, so that emblems read as plates set on it), its edge rounded
# (a quarter round of BEVEL), its wall straight down (towards the ball's middle) into the ball. Built from rings: the
# shape's outline and the outlines inside it at the bevel's depths and every INNER_STEP further (so that the top
# follows the dome), each pair of neighbouring rings filled.

DOME_R = 13.0
DOME_TOP = ORB_R[2] - 0.15
INNER_STEP = 0.85


def dome(x, y):
    """The height of the reliefs' dome at view (x, y)."""
    return DOME_TOP - ((x - ORB_C.x) ** 2 + (y - ORB_C.y) ** 2) / (2 * DOME_R)


def _orient_up(bm):
    """Winds an open relief's faces consistently, each island so that its top faces the camera (+z)."""
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    seen = set()
    for start in bm.faces:
        if start in seen:
            continue
        island, todo = [], [start]
        seen.add(start)
        while todo:
            f = todo.pop()
            island.append(f)
            for e in f.edges:
                for g in e.link_faces:
                    if g not in seen:
                        seen.add(g)
                        todo.append(g)
        if sum(f.normal.z * f.calc_area() for f in island) < 0:
            bmesh.ops.reverse_faces(bm, faces=island)


def _base_normal(base, x, y, e=0.05):
    gx = (base(x + e, y) - base(x - e, y)) / (2 * e)
    gy = (base(x, y + e) - base(x, y - e)) / (2 * e)
    return Vector((-gx, -gy, 1.0)).normalized()


def relief(name, shape, top, mat, bevel=0.35, segments=3, base=dome, sink=0.6, inner=4, profile=None,
           spacing=0.8, hollow=None):
    """A raised part of a symbol: shape a 2D field (inside < 0), its top `top` over base(x, y), the edge rounded by
    a quarter round of bevel (segments steps), the wall reaching sink below the ball's surface. profile: instead of
    the bevel, [(depth inside the outline, height under the top), ...] from the outline in (a custom edge); inner:
    how many rings inside the edge (every INNER_STEP) let the top follow the base; hollow: a depth from the
    outline past which the top is left open (for settings under other parts, which hide it). The wall has no floor
    (it ends inside the ball). The normals are the shape's own (from the outline's distance and the edge's profile),
    not the triangles' (the rings' fills are uneven). Returns the object, or None if the shape is empty."""
    loops = contours(shape, spacing=spacing)
    if not loops:
        return None
    exact = outline_field(loops)
    if profile is None:
        profile = [(bevel * (1 - math.cos(a)), bevel * (1 - math.sin(a)))
                   for a in [math.pi / 2 * i / segments for i in range(segments + 1)]]
    deepest = profile[-1][0]
    profile = list(profile) + [(deepest + INNER_STEP * (i + 1), profile[-1][1]) for i in range(inner)]
    # Each ring's slope: (outward, up) parts of its normal, from the profile's tangent.
    slopes = []
    for i in range(len(profile)):
        (d0, u0), (d1, u1) = profile[max(0, i - 1)], profile[min(len(profile) - 1, i + 1)]
        ds, dh = d1 - d0, -(u1 - u0)
        length = math.hypot(ds, dh) or 1.0
        slopes.append((dh / length, ds / length))
    rings = []
    for (depth, under), slope in zip(profile, slopes):
        ring = loops if depth <= 1e-9 else contours(exact, -depth, spacing=spacing)
        if not ring:
            break
        rings.append((ring, top - under, slope))
    if hollow is not None:
        hole = contours(exact, -hollow, spacing=spacing)
    bm = bmesh.new()
    normals = {}
    ring_edges, ring_verts = [], []
    for ring, height, (out, up) in rings:
        edges, verts = [], []
        for loop, _ in ring:
            vs = [bm.verts.new((x, y, base(x, y) + height)) for x, y in loop]
            edges += [bm.edges.new((vs[i], vs[(i + 1) % len(vs)])) for i in range(len(vs))]
            verts.append(vs)
            xs = np.array([x for x, _ in loop])
            ys = np.array([y for _, y in loop])
            e = 0.04
            gx = (exact(xs + e, ys) - exact(xs - e, ys)) / (2 * e)
            gy = (exact(xs, ys + e) - exact(xs, ys - e)) / (2 * e)
            for v, (x, y), a, b in zip(vs, loop, gx, gy):
                n_out = Vector((a, b, 0.0))
                n_out = n_out.normalized() if n_out.length > 1e-6 else Vector((0.0, 0.0, 0.0))
                normals[v] = (n_out * out + _base_normal(base, x, y) * up).normalized()
        ring_edges.append(edges)
        ring_verts.append(verts)
    for a, b in zip(ring_edges, ring_edges[1:]):
        bmesh.ops.triangle_fill(bm, use_beauty=True, use_dissolve=False, edges=a + b, normal=(0.0, 0.0, 1.0))
    if hollow is not None and hole:
        # Open past `hollow`: the last ring's band down to a ring at that depth, sunk into the ball.
        edges = []
        height = rings[-1][1]
        for loop, _ in hole:
            vs = [bm.verts.new((x, y, base(x, y) + height - 0.25)) for x, y in loop]
            edges += [bm.edges.new((vs[i], vs[(i + 1) % len(vs)])) for i in range(len(vs))]
            for v in vs:
                normals[v] = _base_normal(base, v.co.x, v.co.y)
        bmesh.ops.triangle_fill(bm, use_beauty=True, use_dissolve=False, edges=ring_edges[-1] + edges,
                                normal=(0.0, 0.0, 1.0))
    else:
        bmesh.ops.triangle_fill(bm, use_beauty=True, use_dissolve=False, edges=ring_edges[-1],
                                normal=(0.0, 0.0, 1.0))
    # The wall down into the ball.
    for vs in ring_verts[0]:
        low = [bm.verts.new((v.co.x, v.co.y, min(v.co.z - 0.3, orb_surface(v.co.x, v.co.y) - sink))) for v in vs]
        n = len(vs)
        for i in range(n):
            bm.faces.new((vs[i], vs[(i + 1) % n], low[(i + 1) % n], low[i]))
        for v, w in zip(vs, low):
            normals[w] = Vector((normals[v].x, normals[v].y, 0.0)).normalized() if normals[v].xy.length > 1e-6 \
                else Vector((0.0, 0.0, -1.0))
    _orient_up(bm)
    bm.verts.index_update()
    order = [normals.get(v, Vector((0.0, 0.0, 1.0))) for v in bm.verts]
    obj = kit.from_bmesh(name, bm, mat)
    mesh = obj.data
    for poly in mesh.polygons:
        poly.use_smooth = True
    mesh.normals_split_custom_set_from_vertices([tuple(n) for n in order])
    return obj


_EXACT = {}


def exact(shape):
    """The exact signed distance to a shape's outline (cached)."""
    if shape not in _EXACT:
        _EXACT[shape] = outline_field(contours(shape))
    return _EXACT[shape]


def rounded(shape, convex=0.0, concave=0.0):
    """A shape with its corners rounded: those pointing out by convex, those pointing in by concave."""
    f = exact(shape)
    if convex > 0:
        f = grow(exact(grow(f, -convex)), convex)
    if concave > 0:
        f = grow(exact(grow(f, concave)), -concave)
    return exact(f)


def mirror_half(points):
    """A polygon symmetric about x = 0 from its right half [(x, y), ...] from the top down (x >= 0)."""
    right = [(x, y) for x, y in points]
    left = [(-x, y) for x, y in reversed(points) if x > 1e-9]
    return right + left


def round_profile(width, height, steps=6, power=1.0):
    """An edge rising over width from the outline in, height high, as a quarter ellipse (power > 1: fuller)."""
    out = []
    for i in range(steps + 1):
        a = math.pi / 2 * i / steps
        out.append((width * (1 - math.cos(a)), height * (1 - math.sin(a) ** (1 / power))))
    return out


def paint(obj, field, borders, mats):
    """Cuts an object's faces along the contours field(xs, ys, zs) = border (field takes and gives arrays) and gives
    each face the material of its band (mats[i]: the faces whose middle is past i borders; None keeps theirs)."""
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    for t in borders:
        verts = bm.verts[:]
        co = np.array([v.co for v in verts])
        values = field(co[:, 0], co[:, 1], co[:, 2])
        kit.split_along(bm, dict(zip(verts, values.tolist())), t)
    slots = [None if m is None else kit.slot_of(obj, m) for m in mats]
    faces = bm.faces[:]
    centres = np.array([f.calc_center_median() for f in faces])
    values = field(centres[:, 0], centres[:, 1], centres[:, 2])
    for f, value in zip(faces, values):
        slot = slots[int(sum(value > t for t in borders))]
        if slot is not None:
            f.material_index = slot
    bm.to_mesh(obj.data)
    bm.free()
    kit.drop_unused_materials(obj)
    return obj


def depth_of(shape):
    """A painting field: how deep inside the shape's outline a point is."""
    f = exact(shape)
    return lambda x, y, z: -f(x, y)


def material(name, index, metallic=0.2, roughness=0.3, glow=None, strength=0.0):
    """A palette material; glow: the palette index of its light's colour (strength: how strongly)."""
    if glow is None:
        return k.material(name, palette=index, metallic=metallic, roughness=roughness)
    return k.material(name, palette=index, metallic=metallic, roughness=roughness,
                      emission=k.level_palette()[glow], emission_strength=strength)


def flame(cx, cy, w, up, down=None):
    """A drop pointing up: round below (w across either way, down below its middle), drawn to a point up above
    (cx, cy)."""
    down = w if down is None else down
    return blend(ellipse(cx, cy, w, down), polygon([(cx - w * 0.75, cy), (cx + w * 0.75, cy), (cx, cy + up)]), 0.35)


def glowing(name, index, glow, strength, metallic=0.1, roughness=0.2):
    return material(name, index, metallic, roughness, glow=glow, strength=strength)


def gem(name, shape, mats, top, height=0.8, core=0.45):
    """A small domed amber gem: its rim orange, its heart yellow (mats: [rim, heart]); top: over the dome."""
    obj = relief(name, shape, top, mats[0], profile=round_profile(0.9, height, 4), inner=1, spacing=0.35)
    return paint(obj, depth_of(shape), [core], mats)


# --- The badges: Pulse-Cannon (P), Multi-Cannon (M), Hyper Pulse (H) ---------------------------------------------
# A red enamel badge on a dark setting (the sprite's dark outline), its middle sunk as a dark red field (P, M) where
# the light letter stands, glowing amber gems where the sprite is brightest (the crest; the M's wings); the H stands
# on the red in its own dark outline (the sprite's 0x50 round it).

BADGE_HEIGHTS = dict(setting=0.45, badge=1.25, field=0.8, letter_outline=1.45, letter=1.95, gem=2.1)
SETTING_W = 0.8      # the dark setting round the badge (the sprite's outline pixels)
FRAME_W = 1.05       # the red frame round the sunk field


def badge_materials():
    return dict(
        setting=material("badge_setting", 0x41, 0.4, 0.3),
        badge=material("badge_red", 0x77, 0.3, 0.24),
        field=material("badge_field", 0x73, 0.25, 0.3),
        outline=material("letter_outline", 0x50, 0.3, 0.3),
        letter=[material("letter_top", 0x5f, 0.35, 0.22), material("letter_mid", 0x5d, 0.35, 0.22),
                material("letter_low", 0x5b, 0.35, 0.24)],
        gem=[glowing("gem_rim", 0x78, 0x79, 0.45), glowing("gem_heart", 0x7c, 0x7d, 0.6)],
    )


def letter_relief(shape, mats, top):
    """A letter: light metal shading darker downwards (the sprite's 0x5f-0x57 from its top row down)."""
    obj = relief("letter", rounded(shape, 0.3, 0.2), top, mats["letter"][0], bevel=0.38, segments=3, inner=2)
    return paint(obj, lambda x, y, z: -y, [-1.4, 0.4], mats["letter"])


def badge(outline, mats, field_shape=None, letter=None, letter_outline=None, gems=()):
    """A badge: its outer outline (the setting's), the red badge inside it, the sunk field, the letter and gems
    (shapes)."""
    h = BADGE_HEIGHTS
    outer = rounded(outline, 0.2, 0.35)
    red = grow(outer, -SETTING_W)
    parts = [relief("badge_setting", outer, h["setting"], mats["setting"], bevel=0.3, segments=2, inner=0,
                    hollow=SETTING_W + 0.9)]
    if field_shape is not None:
        field_shape = rounded(field_shape, 0.4, 0.3)
        parts.append(relief("badge", minus(red, field_shape), h["badge"], mats["badge"], bevel=0.42, segments=3,
                            inner=2))
        parts.append(relief("badge_field", field_shape, h["field"], mats["field"], bevel=0.2, segments=2, inner=2))
    else:
        parts.append(relief("badge", red, h["badge"], mats["badge"], bevel=0.42, segments=3, inner=3))
    if letter_outline is not None:
        parts.append(relief("letter_outline", rounded(letter_outline, 0.3, 0.2), h["letter_outline"],
                            mats["outline"], bevel=0.2, segments=2, inner=1))
    if letter is not None:
        parts.append(letter_relief(letter, mats, h["letter"]))
    for i, shape in enumerate(gems):
        parts.append(gem(f"gem{i}", shape, mats["gem"], h["gem"]))
    return [p for p in parts if p is not None]


P_OUTLINE = mirror_half([(0.0, 8.6), (1.0, 7.6), (2.0, 6.7), (3.4, 6.05), (5.0, 5.6), (6.0, 4.9), (6.9, 4.0),
                         (7.0, 3.2), (7.0, -3.0), (6.4, -4.0), (6.1, -5.0), (5.2, -6.1), (4.1, -6.6),
                         (3.1, -6.1), (2.2, -5.0), (1.6, -4.25), (0.0, -4.0)])
P_LETTER = union(box(-4.15, -1.95, -2.3, 4.2),
                 minus(union(box(-4.15, 1.55, -0.05, 4.2), circle(1.55, 2.075, 2.125)),
                       union(box(-1.95, 1.55, 1.3, 2.85), circle(1.55, 2.075, 0.775))))


def pulse_cannon():
    """153: a white P on a red badge, an amber flame in its crest."""
    mats = badge_materials()
    field = intersect(grow(polygon(P_OUTLINE), -SETTING_W - FRAME_W), box(-8.0, 8.0, -3.35, 4.65))
    return badge(polygon(P_OUTLINE), mats, field_shape=field, letter=P_LETTER, gems=[flame(0.0, 5.6, 1.0, 2.1)])


M_OUTLINE = mirror_half([(0.0, 7.5), (1.1, 6.7), (2.1, 5.8), (3.0, 4.6), (3.6, 4.05), (4.4, 4.3), (5.3, 5.2),
                         (6.8, 5.5), (7.7, 4.4), (8.6, 3.1), (9.1, 2.0), (8.9, 1.0), (8.1, 0.2), (8.0, -1.8),
                         (7.1, -2.8), (6.2, -3.6), (6.0, -4.8), (5.1, -5.7), (4.3, -6.7), (3.2, -7.3),
                         (1.8, -6.7), (1.0, -5.6), (0.6, -5.0), (0.0, -4.9)])
M_LETTER = intersect(union(box(-5.0, -3.0, -3.0, 3.0), box(3.0, 5.0, -3.0, 3.0),
                           capsule(-4.0, 2.0, 0.0, -0.35, 1.02), capsule(4.0, 2.0, 0.0, -0.35, 1.02)),
                     box(-5.0, 5.0, -3.0, 3.0))


def multi_cannon():
    """155: a white M on a red winged badge, amber flames in its crest and wings."""
    mats = badge_materials()
    field = intersect(grow(polygon(M_OUTLINE), -SETTING_W - FRAME_W), box(-6.4, 6.4, -4.4, 3.6))
    return badge(polygon(M_OUTLINE), mats, field_shape=field, letter=M_LETTER,
                 gems=[flame(0.0, 3.2, 0.95, 2.4), flame(-6.5, 1.4, 0.75, 1.7), flame(6.5, 1.4, 0.75, 1.7)])


H_OUTLINE = mirror_half([(0.0, 9.3), (1.2, 8.5), (6.6, 3.2), (7.0, 2.4), (7.0, -3.8), (6.5, -5.0), (5.3, -6.7),
                         (4.0, -8.2), (3.0, -7.5), (2.1, -6.0), (1.3, -4.6), (0.8, -4.1), (0.0, -4.0)])
H_LETTER = union(box(-4.0, -2.0, -2.0, 5.0), box(2.0, 4.0, -2.0, 5.0), box(-4.0, 4.0, 1.0, 3.0))


def hyper_pulse():
    """269: a white H on a red badge pointing up, an amber flame in its point."""
    mats = badge_materials()
    return badge(polygon(H_OUTLINE), mats, letter=H_LETTER, letter_outline=grow(H_LETTER, 0.9),
                 gems=[flame(0.0, 5.8, 1.25, 2.4)])


# --- Mega Cannon: a fireball ---------------------------------------------------------------------------------------
# The sprite's ball of fire (columns 6-17, rows 6-17: round (0, 2), 6 across either way with its dark rim) with
# three tongues of fire licking down from it (columns 8, 10-13 and 15, rows 18-20): a dome of fire glowing white-hot
# in its middle, through yellow and orange to red at its edge (the sprite's 0x7f out to 0x73), the borders wavering
# like flames; on a dark setting (the sprite's 0xa1, 0x41, 0x40 round it).

FIRE = blend(circle(0.0, 2.0, 5.95),
             union(polygon([(-2.5, -2.6), (2.5, -2.6), (1.5, -5.4), (0.0, -7.4), (-1.5, -5.4)]),
                   polygon([(-4.9, -2.2), (-2.7, -2.4), (-2.9, -5.0), (-3.6, -7.2), (-4.4, -5.0)]),
                   polygon([(4.9, -2.2), (2.7, -2.4), (2.9, -5.0), (3.6, -7.2), (4.4, -5.0)])), 0.9)
# The bands from the edge in (depth inside the fire's outline) and their colours (palette, glow, strength).
FIRE_BANDS = [0.75, 1.65, 2.45, 3.25]
FIRE_COLOURS = [(0x75, 0x76, 0.36), (0x79, 0x7a, 0.42), (0x7c, 0x7c, 0.5), (0x7e, 0x7e, 0.55), (0x7f, 0x7f, 0.6)]


def mega_cannon():
    """157: a fireball."""
    setting = material("fire_setting", 0xa1, 0.2, 0.4)
    mats = [glowing(f"fire{i}", index, glow, strength, 0.0, 0.3) for i, (index, glow, strength) in
            enumerate(FIRE_COLOURS)]
    shape = rounded(FIRE, 0.2, 0.6)
    fire = grow(shape, -0.75)
    parts = [relief("fire_setting", shape, 0.4, setting, bevel=0.3, segments=2, inner=0, hollow=1.6),
             relief("fire", fire, 2.9, mats[0], profile=round_profile(4.4, 2.5, 7, power=1.3), inner=1, spacing=0.5)]
    depth = depth_of(fire)

    def wavering(x, y, z):
        a = np.arctan2(y - 2.0, x)
        return depth(x, y, z) + 0.28 * np.sin(5 * a + 1.3) + 0.16 * np.sin(9 * a + 0.4)
    paint(parts[1], wavering, FIRE_BANDS, mats)
    return parts


# --- Laser: a glowing rod -----------------------------------------------------------------------------------------
# The sprite's rod of light (columns 7-16, rows 5-21, its ends cut off at 45 degrees): a crystal rod lying on the
# ball, round across, glowing white-hot along its middle (the sprite's 0x7f, two columns), through yellow and orange
# to red at its sides (0x7c, 0x79, 0x75), on a dark red setting (its 0x71 outline).

ROD = polygon([(-2.0, 9.0), (2.0, 9.0), (5.0, 6.0), (5.0, -5.0), (2.0, -8.0), (-2.0, -8.0), (-5.0, -5.0), (-5.0, 6.0)])
ROD_BANDS = [0.75, 1.45, 2.15, 2.85, 3.45]
ROD_COLOURS = [(0x74, 0x75, 0.34), (0x77, 0x78, 0.4), (0x79, 0x7a, 0.45), (0x7b, 0x7c, 0.5), (0x7d, 0x7e, 0.55),
               (0x7f, 0x7f, 0.6)]


def laser():
    """159: a glowing rod."""
    setting = material("rod_setting", 0x71, 0.3, 0.3)
    mats = [glowing(f"rod{i}", index, glow, strength, 0.0, 0.2) for i, (index, glow, strength) in
            enumerate(ROD_COLOURS)]
    shape = rounded(ROD, 1.2, 0.0)
    rod = grow(shape, -0.7)
    parts = [relief("rod_setting", shape, 0.4, setting, bevel=0.3, segments=2, inner=0, hollow=1.6),
             relief("rod", rod, 3.0, mats[0], profile=round_profile(4.3, 2.6, 7), inner=0)]
    paint(parts[1], depth_of(rod), ROD_BANDS, mats)
    return parts


# --- Zica Laser: a blue crystal drop ------------------------------------------------------------------------------
# The sprite's drop (columns 5-18, rows 3-22: round above, pointed below): a cabochon of blue crystal, deep blue at its
# edge (the sprite's 0x92-0x95), lighter inwards (0x98-0x9f), its heart in the upper middle glowing pale cyan to white
# (0x8a-0x8f); on a dark navy setting (its 0x90, 0x32, 0x51 outline).

DROP = polygon(mirror_half([(0.0, 11.0), (2.6, 10.6), (4.4, 9.6), (5.8, 8.2), (6.7, 6.4), (7.0, 4.4), (6.9, 2.0),
                            (6.4, -0.5), (5.6, -2.8), (4.5, -5.0), (3.2, -7.0), (1.8, -8.6), (0.6, -9.6),
                            (0.0, -9.95)]))
DROP_HEART = ellipse(0.0, 5.0, 3.3, 4.1)
DROP_HEART_CORE = ellipse(0.0, 5.6, 1.8, 2.4)
DROP_HALO = 0.95     # the light blue ring round the heart


def zica_laser():
    """161: a blue crystal drop with a glowing heart."""
    setting = material("drop_setting", 0x91, 0.3, 0.3)
    body = [glowing("drop0", 0x94, 0x96, 0.2, 0.1, 0.12), glowing("drop1", 0x98, 0x99, 0.26, 0.1, 0.12),
            glowing("drop2", 0x9c, 0x9d, 0.32, 0.1, 0.12)]
    heart = [glowing("drop_halo", 0x9f, 0x8a, 0.4, 0.05, 0.12), glowing("drop_heart", 0x8c, 0x8c, 0.46, 0.05, 0.12),
             glowing("drop_core", 0x8f, 0x8f, 0.56, 0.05, 0.12)]
    shape = rounded(DROP, 0.0, 0.0)
    drop = grow(shape, -0.75)
    parts = [relief("drop_setting", shape, 0.4, setting, bevel=0.3, segments=2, inner=0, hollow=1.6),
             relief("drop", drop, 3.1, body[0], profile=round_profile(5.0, 2.8, 7), inner=1, spacing=0.55)]
    paint(parts[1], depth_of(drop), [0.85, 2.0], body)
    heart_field = exact(DROP_HEART)
    core_field = exact(DROP_HEART_CORE)
    paint(parts[1], lambda x, y, z: -heart_field(x, y), [-DROP_HALO, 0.0], [None, heart[0], heart[1]])
    paint(parts[1], lambda x, y, z: -core_field(x, y), [0.0], [None, heart[2]])
    return parts


# --- Protron: three bubbles ---------------------------------------------------------------------------------------
# The sprite's three pale bubbles (the middle one larger and higher: columns 9-14, rows 8-14; the others columns 4-8
# and 15-19, rows 12-16) in a dark socket round them all (its 0x01-0x03, 0x52 outline): glossy pearls of pale cyan
# (0x8a, lit from the sun; glowing a little, so that their shaded side stays pale).

BUBBLES = [(0.0, 2.5, 3.45), (-5.5, -0.5, 2.6), (5.5, -0.5, 2.6)]


def protron():
    """163: three pale bubbles."""
    setting = material("bubble_socket", 0x63, 0.3, 0.3)
    pearl = glowing("bubble", 0x8b, 0x8a, 0.32, 0.05, 0.08)
    socket = rounded(union(*[circle(x, y, r + 0.8) for x, y, r in BUBBLES]), 0.0, 0.8)
    parts = [relief("bubble_socket", socket, 0.5, setting, bevel=0.3, segments=2, inner=0, hollow=1.7)]
    for i, (x, y, r) in enumerate(BUBBLES):
        parts.append(relief(f"bubble{i}", circle(x, y, r), 0.6 + r * 0.8, pearl,
                            profile=round_profile(r * 0.98, r * 0.8, 8), inner=0, spacing=0.4))
    return parts


# --- Vulcan Cannon: three bullets ---------------------------------------------------------------------------------
# The sprite's three bullets flying up, staggered (columns 10-14 from row 5, 14-18 from row 8, 6-10 from row 11),
# each round at its nose and tapering to its tail, red with a hot stripe along its top (the sprite's middle column:
# yellow 0x7c at the nose to 0x77 at the tail), on a dark setting (0x41, 0x10, 0x70 round them).

BULLETS = [(0.5, 9.0), (4.5, 6.0), (-3.5, 3.0)]   # (x, top) of each


def bullet_shape(x, top):
    """A bullet nose up: round at its nose, straight, tapering to a point at its tail (11 pixels long)."""
    return blend(capsule(x, top - 2.45, x, top - 5.6, 2.45),
                 polygon([(x - 2.45, top - 5.6), (x + 2.45, top - 5.6), (x + 1.2, top - 9.2), (x, top - 11.3),
                          (x - 1.2, top - 9.2)]), 0.5)


def vulcan():
    """165: three bullets."""
    setting = material("bullet_setting", 0x41, 0.3, 0.3)
    body = [glowing("bullet0", 0x74, 0x75, 0.22, 0.3, 0.22), glowing("bullet1", 0x77, 0x78, 0.3, 0.3, 0.22)]
    stripe = [glowing("bullet_tail", 0x76, 0x77, 0.38, 0.2, 0.2), glowing("bullet_mid", 0x79, 0x7a, 0.46, 0.2, 0.2),
              glowing("bullet_nose", 0x7c, 0x7d, 0.58, 0.2, 0.2)]
    shapes = [bullet_shape(x, top) for x, top in BULLETS]
    parts = [relief("bullet_setting", rounded(union(*shapes), 0.0, 0.4), 0.45, setting, bevel=0.3, segments=2,
                    inner=1)]
    for i, ((x, top), shape) in enumerate(zip(BULLETS, shapes)):
        b = grow(shape, -0.7)
        obj = relief(f"bullet{i}", b, 2.4, body[0], profile=round_profile(1.75, 1.85, 5), inner=0, spacing=0.6)
        depth = depth_of(b)
        paint(obj, depth, [0.55], body)

        def along(xs, ys, zs, depth=depth, top=top):
            d = depth(xs, ys, zs)
            return np.where(d > 1.05, ys - (top - 8.0), -99.0)
        paint(obj, along, [-98.0, 2.4, 5.4], [None] + stripe)
        parts.append(obj)
    return parts


# --- Lightning Cannon: a bolt of blue plasma ----------------------------------------------------------------------
# The sprite's bolt (rows 3-24: from columns 7-14 at the top, forked at row 3, bending down to columns 11-17 at the
# bottom, where it reaches a pixel past the ball): a ribbon of blue plasma, darker at its edges (0x90-0x94), lighter
# inwards (0x97-0x9c), with a white-hot streak running down it (the sprite's 0x3e/0x3f down column 9, then 0x9f-0x9c
# crossing to column 15: the ribbon's twist), its crest following the streak.

BOLT = polygon([(4.0, 11.0), (3.4, 10.0), (3.0, 8.5), (2.6, 7.0), (2.2, 5.0), (2.7, 3.0), (3.6, 1.2), (4.6, -0.5),
                (5.4, -2.3), (6.0, -4.0), (6.1, -6.5), (5.6, -8.2), (4.6, -9.6), (3.0, -10.6), (1.6, -11.0),
                (0.9, -10.0), (0.6, -8.5), (-0.4, -7.2), (-1.4, -5.8), (-2.6, -4.2), (-3.7, -2.6), (-4.3, -0.8),
                (-4.9, 1.0), (-5.0, 4.5), (-5.0, 7.5), (-4.6, 9.0), (-4.0, 10.2), (-3.6, 11.0), (-0.2, 11.0),
                (0.4, 10.1), (1.0, 11.0)])
STREAK = [(-1.6, 9.4), (-2.4, 8.0), (-2.6, 6.5), (-2.55, 4.0), (-2.4, 2.4), (-2.0, 0.9), (-1.45, -0.5),
          (-0.6, -1.9), (0.5, -3.1), (1.6, -4.3), (2.6, -5.5), (3.3, -6.6), (3.6, -7.8)]


def path_distance(points):
    """A field: the distance from a polyline."""
    def f(x, y):
        x = np.asarray(x, float)
        y = np.asarray(y, float)
        d = np.full(np.broadcast(x, y).shape, np.inf)
        for (ax, ay), (bx, by) in zip(points, points[1:]):
            ex, ey = bx - ax, by - ay
            wx, wy = x - ax, y - ay
            t = np.clip((wx * ex + wy * ey) / (ex * ex + ey * ey), 0.0, 1.0)
            d = np.minimum(d, np.hypot(wx - ex * t, wy - ey * t))
        return d
    return f


def lightning():
    """167: a bolt of blue plasma."""
    setting = material("bolt_setting", 0x90, 0.3, 0.3)
    body = [glowing("bolt0", 0x92, 0x94, 0.28, 0.1, 0.18), glowing("bolt1", 0x96, 0x98, 0.34, 0.1, 0.18),
            glowing("bolt2", 0x9b, 0x9c, 0.42, 0.1, 0.18)]
    streak = [glowing("bolt_streak", 0x9e, 0x9f, 0.5, 0.05, 0.15), glowing("bolt_core", 0x3f, 0x3e, 0.6, 0.05, 0.15)]
    shape = rounded(BOLT, 0.35, 0.5)
    bolt = grow(shape, -0.7)
    along = path_distance(STREAK)

    def base(x, y):
        # The crest follows the streak: the ribbon rises towards it.
        d = float(along(x, y))
        return dome(x, y) + 0.55 * max(0.0, 1.0 - d / 3.0)
    parts = [relief("bolt_setting", shape, 0.4, setting, bevel=0.3, segments=2, inner=0, hollow=1.5),
             relief("bolt", bolt, 2.1, body[0], base=base, profile=round_profile(2.0, 1.5, 6), inner=1, spacing=0.5)]
    paint(parts[1], depth_of(bolt), [0.6, 1.3], body)
    paint(parts[1], lambda x, y, z: -along(x, y), [-1.15, -0.5], [None] + streak)
    return parts


# --- Missile Launcher and Heavy Missile Launcher: rockets ---------------------------------------------------------
# Rockets lying on the ball, nose up: lathed bodies (profiles of (y, radius) from the tail up, as the sprites' rows
# draw them), bent with the dome, their fins flat plates at their sides, on a dark setting (the sprites' outlines).

def rocket_body(name, profile, mat, axis_z, segments=28, squash=0.8):
    obj = k.lathe(name, profile, mat, segments, axis_x=0.0, axis_z=0.0, squash=squash)
    for v in obj.data.vertices:
        v.co.z += dome(v.co.x, v.co.y) + axis_z
    obj.data.update()
    return k.smooth(obj, 50.0)


def silhouette(profile):
    """The plan of a lathed body (profile [(y, radius), ...] from the tail up)."""
    right = [(r, y) for y, r in reversed(profile)]
    return polygon(right + [(-r, y) for y, r in profile])


MISSILE = [(-5.2, 0.0), (-5.05, 1.1), (-4.6, 1.6), (-4.0, 2.2), (-2.6, 2.45), (-1.2, 2.55), (-0.5, 2.25),
           (0.2, 1.95), (1.6, 1.95), (2.25, 2.4), (2.9, 2.85), (3.9, 2.85), (4.7, 2.5), (5.5, 2.0), (6.3, 1.4),
           (6.9, 0.75), (7.15, 0.0)]
MISSILE_FIN = [(1.9, -0.5), (2.7, -1.1), (4.5, -3.3), (4.85, -4.9), (4.35, -6.2), (3.65, -6.8), (3.0, -5.7),
               (2.2, -4.9)]


def missile():
    """201: a grey rocket with a dark seeker in its nose and swept fins."""
    setting = material("rocket_setting", 0x03, 0.3, 0.35)
    grey = [material("rocket_nozzle", 0x05, 0.4, 0.3), material("rocket_tail", 0x0c, 0.3, 0.24),
            material("rocket_neck", 0x0b, 0.3, 0.24), material("rocket_head", 0x0e, 0.3, 0.22),
            glowing("rocket_seeker", 0x62, 0x66, 0.25, 0.4, 0.12)]
    fin_mat = grey[1]     # the fins in the tail's grey
    fins = [polygon(MISSILE_FIN), polygon([(-x, y) for x, y in MISSILE_FIN])]
    plan = union(silhouette(MISSILE), *fins)
    parts = [relief("rocket_setting", rounded(grow(plan, 0.75), 0.0, 0.5), 0.4, setting, bevel=0.3, segments=2,
                    inner=1)]
    for i, fin in enumerate(fins):
        parts.append(relief(f"rocket_fin{i}", rounded(fin, 0.3, 0.0), 1.2, fin_mat, bevel=0.3, segments=2, inner=1))
    body = rocket_body("rocket", MISSILE, grey[1], 0.9)
    paint(body, lambda x, y, z: y, [-4.35, -0.55, 2.15], grey[:4])
    # The seeker: a dark slot down the nose between two light lobes (the sprite's 0x02-0x05 at columns 11-12 of
    # rows 7-9, its light 0x06/0x0a beside them).
    paint(body, lambda x, y, z: np.minimum(y - 4.75, 0.85 - np.abs(x)), [0.0], [None, grey[4]])
    parts.append(body)
    return parts


HEAVY = [(-4.8, 0.0), (-4.6, 1.0), (-4.1, 1.5), (-3.3, 1.9), (-2.3, 2.25), (-1.2, 2.45), (-0.4, 2.5), (0.0, 2.55),
         (0.35, 2.05), (0.9, 1.95), (1.45, 2.05), (1.8, 2.6), (2.4, 2.95), (3.4, 3.0), (4.5, 2.8), (5.6, 2.45),
         (6.6, 2.0), (7.3, 1.35), (7.75, 0.6), (7.95, 0.0)]
HEAVY_FIN = [(1.6, -1.6), (2.4, -2.2), (3.7, -3.3), (3.75, -4.9), (3.0, -5.8), (2.0, -5.0), (1.5, -4.3)]


def heavy_missile():
    """203: a green rocket with a gold band and brown fins."""
    setting = material("heavy_setting", 0x21, 0.3, 0.35)
    body_mats = [material("heavy_nozzle", 0x13, 0.3, 0.3), material("heavy_tail", 0x28, 0.25, 0.24),
                 material("heavy_band", 0xbb, 0.5, 0.22), material("heavy_ring", 0xbe, 0.5, 0.2),
                 material("heavy_band", 0xbb, 0.5, 0.22), material("heavy_shell", 0x2a, 0.25, 0.22)]
    fin_mat = material("heavy_fin", 0x19, 0.3, 0.26)
    fins = [polygon(HEAVY_FIN), polygon([(-x, y) for x, y in HEAVY_FIN])]
    plan = union(silhouette(HEAVY), *fins)
    parts = [relief("heavy_setting", rounded(grow(plan, 0.75), 0.0, 0.5), 0.4, setting, bevel=0.3, segments=2,
                    inner=1)]
    for i, fin in enumerate(fins):
        parts.append(relief(f"heavy_fin{i}", rounded(fin, 0.3, 0.0), 1.2, fin_mat, bevel=0.3, segments=2, inner=1))
    body = rocket_body("heavy", HEAVY, body_mats[1], 0.9)
    paint(body, lambda x, y, z: y, [-3.9, -0.45, 0.55, 1.25, 2.05], body_mats)
    parts.append(body)
    return parts


# --- Guided Bombs: a bomb with a seeker eye -----------------------------------------------------------------------
# The sprite's round bomb (columns 6-17, rows 8-19, round (0, 0)): a domed steel casing (its 0x34-0x3f, lit at the
# upper left) on a dark rim (0x01, 0x02, 0x31, 0x50), a four-pointed star of lighter steel over it (the upscale's
# lighter pattern), and in its middle the red seeker eye glowing hottest a little to the upper left (the sprite's
# 0x7d at row 13, column 11), in a dark socket.

BOMB_R = 6.0
STAR = polygon([(0.0, 4.9), (1.25, 1.25), (4.9, 0.0), (1.25, -1.25), (0.0, -4.9), (-1.25, -1.25), (-4.9, 0.0),
                (-1.25, 1.25)])
EYE = (0.0, 0.0, 1.95)


def guided_bombs():
    """267: a bomb with a red seeker eye."""
    setting = material("bomb_setting", 0x31, 0.35, 0.3)
    steel = material("bomb_casing", 0x3a, 0.35, 0.24)
    star_mat = material("bomb_star", 0x3d, 0.35, 0.2)
    socket = material("bomb_socket", 0x30, 0.3, 0.3)
    eye = [glowing("bomb_eye0", 0x75, 0x76, 0.4, 0.1, 0.12), glowing("bomb_eye1", 0x79, 0x7a, 0.5, 0.1, 0.12),
           glowing("bomb_eye2", 0x7d, 0x7e, 0.6, 0.1, 0.12)]
    ex, ey, er = EYE
    parts = [relief("bomb_setting", circle(0.0, 0.0, BOMB_R), 0.4, setting, bevel=0.3, segments=2, inner=0,
                    hollow=1.6),
             relief("bomb", circle(0.0, 0.0, BOMB_R - 0.75), 1.9, steel, profile=round_profile(3.2, 1.5, 6),
                    inner=1, spacing=0.5),
             relief("bomb_star", rounded(STAR, 0.25, 0.4), 2.3, star_mat, bevel=0.3, segments=2, inner=1),
             relief("bomb_socket", circle(ex, ey, er + 0.55), 2.45, socket, bevel=0.25, segments=2, inner=0)]
    lens = relief("bomb_eye", circle(ex, ey, er), 3.3, eye[0], profile=round_profile(er * 0.95, 1.0, 5), inner=0,
                  spacing=0.35)
    hot = circle(ex - 0.35, ey + 0.35, 1.0)
    paint(lens, lambda x, y, z: -hot(x, y), [-0.75, 0.0], eye)
    parts.append(lens)
    return parts


MODELS = {
    "pu_pulse_cannon": (153, pulse_cannon),
    "pu_multi_cannon": (155, multi_cannon),
    "pu_mega_cannon": (157, mega_cannon),
    "pu_laser": (159, laser),
    "pu_zica_laser": (161, zica_laser),
    "pu_protron": (163, protron),
    "pu_vulcan": (165, vulcan),
    "pu_lightning": (167, lightning),
    "pu_missile": (201, missile),
    "pu_heavy_missile": (203, heavy_missile),
    "pu_guided_bombs": (267, guided_bombs),
    "pu_hyper_pulse": (269, hyper_pulse),
}


# --- Building ----------------------------------------------------------------------------------------------------

ORB_RAMP = 13   # ice blue


def triangulate(objects):
    """Splits every face into triangles (the same split every run, the custom normals kept), so that the export
    doesn't split the n-gons itself (its split changed after a --check render; polish_k_pod.triangulate)."""
    for obj in objects:
        mod = obj.modifiers.new("triangulate", "TRIANGULATE")
        mod.quad_method = "BEAUTY"
        mod.ngon_method = "BEAUTY"
        mod.min_vertices = 4
        mod.keep_custom_normals = True
        kit.apply(obj)
    return objects


def sheet_path(opts):
    sheet = opts["check"]
    return os.path.join(sheet, SHEET) if os.path.isdir(sheet) else sheet


def check_view(opts, name, sprite, objects):
    """The silhouette as the game's camera sees it (the view space's top view, before the tilt) against the
    sprite's pixels: the overlap the models are judged by."""
    if "check" not in opts:
        return None
    mask = kit.sprite_mask(sheet_path(opts), sprite, True)
    return kit.compare("%s (powerups %d) as the game's camera sees it" % (name, sprite),
                       kit.coverage(objects, 24, 28), mask)


def check_top(opts, name, sprite, objects):
    """The silhouette from straight above (after the tilt) against the sprite's pixels."""
    if "check" not in opts:
        return None
    mask = kit.sprite_mask(sheet_path(opts), sprite, True)
    return kit.compare("%s (powerups %d) from straight above" % (name, sprite), kit.coverage(objects, 24, 28), mask)


def build_model(name):
    """The model's parts in the game's axes."""
    sprite, symbol = MODELS[name]
    k.reset()
    parts = [orb(ORB_RAMP)] + symbol()
    for obj in parts:
        kit.drop_unused_materials(obj)
    return sprite, parts


def build():
    opts = kit.options()
    for name in MODELS:
        if not kit.wanted(opts, name):
            continue
        sprite, parts = build_model(name)
        triangulate(parts)
        check_view(opts, name, sprite, parts)
        to_world(parts)
        check_top(opts, name, sprite, parts)
        bpy.context.scene.view_settings.view_transform = "Standard"
        kit.report(name, parts, os.path.join(kit.outdir(opts), name + ".glb"))
        if "preview" in opts:
            kit.preview(opts["preview"] + name, parts, (24, 28), scale=16, distance=0.6)


if __name__ == "__main__":
    build()
