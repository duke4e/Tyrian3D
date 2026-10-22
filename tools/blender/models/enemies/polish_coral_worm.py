"""CORAL's red sea worm and its glossy blue egg (sheet ', written x27 in models.cfg; 2x2 sprites of 24 x 28 pixels;
episode 5, ground enemies, one frame each). Polished (2026-10-21, round 29); it replaces wave3_ae_coral.py's worm and
egg (its last models).

The worm (enemies 1216 and 1217, ' 1 above ' 39, armour 20 each): CORAL sends it 15 times (t 320-5260), always inside
its segmented grey column (polish_coral_pylon.py): 1216 at (x, y + 14) and 1217 at (x, y + 42) of the column's 1213 at
(x, y), type 6 (ground, slots 25-49) while the column's three pieces are type 10 (ground 2, slots 75-99); the game draws
slots 25-49 first, so the column covers it (every one of its 422 pixels lies under the column's). The two swim in from
beyond the screen's edge together; 50 ticks later the worm's link gets eyc 3 and the worm shoots out of the column down
the screen, its pointed end first, while the column accelerates away up the screen. So it is built to lie in the
column's bore, on its floor (WORM_Z), every part of it inside the column's outer surface (--check tests it), and out
of the column it swims a pixel over the sea floor. The two pieces are enemies of their own (one can be shot away
first; shots test the enemies in slot order, so the hidden worm can die before the column).

As its sprites and their 4x upscales draw it (columns and rows of the 24 x 56 picture): a fat red tube (ramp 4), 8
pixels wide (columns 8-15), lit along its top (0x4a-0x4c, a column right of the middle), its flanks 0x45-0x46; ringed
into segments by dark pinches 6 pixels wide (rows 14, 22, 30, 38, 46), each segment's lower rim, just over a pinch,
lighter (0x48-0x49, 0x4b); at its top a knot of three lobes side by side (rows 0-3, 10 pixels wide, each lobe lit at
its left: 0x4b), a narrow neck under it (rows 4-5); at its bottom the pointed end (rows 47-55, narrowing to 2 pixels),
a glossy highlight on it (0x4d-0x4e, rows 48-50).

The egg (enemies 1224 and 1225, ' 14 above ' 52, armour 254 each, value 300): CORAL's boss. 1225 at t5462 and 1224 at
t5490 (28 ticks, 28 pixels above it), at x 92 and 210 (links 10 and 11), into the two dark bays of the domed citadel
(sheet %, models.cfg coral_citadel_*, polish_coral_citadel.py: BAY_U, x -58 and 60), the boss bar following them, event 31
making them fire by turns, the level ending when both are dead. As its sprites draw it: a glossy blue egg (ramp 3)
24 x 48 (rows 3-50: full width over rows 12-41, its ends round), half sunk, darker round its edge (0x35-0x37) and at
its lower corners (0x34-0x36), lighter over its top (0x38-0x39), faint paler veins in a chevron over its middle
(0x39-0x3a), a bright streak of reflected light down its upper right (0x3b-0x3c), and inside it a pale glow at its
middle (rows 24-31: 0x3c-0x3e and white 0x6f in a crescent).

Built as such a creature and such an egg: the worm's body is turned about an axis along y (WORM_Z high; its
cross-sections ellipses WORM_SQUASH times as high as wide), its half widths following the sprites' (the pinches, each
segment's rim bulging a little over its pinch, the neck, the pointed end); the knot three ellipsoid lobes; painted in
ramp 4's shades in bands by how much each part faces up (polish_coral_pylon's turned surfaces, normals analytic), the
rims a shade or two lighter, the pinches darker, a glossy highlight over the pointed end. The egg is a capsule (round
ends of its own half width) lying in the floor, its upper half showing (EGG_H high), glossy; painted for the game's
camera (polish_dark_orb.py's way): each point of it takes the shade the sprite draws where the camera, 20 degrees off
straight down from the bottom of the screen, sees that point (y + z tan 20), from the sprite's shades blurred a
little, in bands cut along smooth contours (polish_orb_red.band_split); the glow's shades (0x3c in the glow, 0x3d,
0x3e, 0x6f) glowing in their own colours (0.18-0.6), the reflected streak not.

Each is built whole and cut along the sprites' edge (y = 0; polish_coral_pylon.cut: the caps keep their material, the
rest the uncut parts' shading; the worm's caps in its flesh 0x46, the egg's in 0x3b glowing faintly (0.2): the
egg's inside, seen when its lower half is shot away), each piece moved so that its sprite's centre is its origin, every
mesh triangulated (polish_k_pod.triangulate: the same output with and without --check) and joined into one mesh.
Deterministic: no random numbers, no booleans.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up from the floor. Each whole's origin is
the middle of its picture's width on the edge between its two sprites: column c is x = c - 11.5, row r is
y = 27.5 - r; the pieces' centres (0, 14) and (0, -14). The worm's whole origin is the column's whole origin (the
middle of T 281): the worm's sprites lie 14 pixels down the column's.

models.cfg (model lines unchanged: coral_worm_t / _b, coral_egg_t / _b enemies/coral_*.glb origin): sprite x27 1
coral_worm_t yaw=0 height=-4 and sprite x27 39 coral_worm_b yaw=0 height=-4 (on the sea floor with its column: drawn
at their origin, ground pieces otherwise float 4 pixels over the terrain); the egg's lines (sprite x27 14 coral_egg_t
yaw=0, sprite x27 52 coral_egg_b yaw=0) keep no height option: they stand 4 pixels over the floor, on the floors of
the citadel's bays (polish_coral_citadel.py: the citadel on the floor with height=-4, its bays' floors at its z 4,
Z_BAY), over the dark pods there. Replaces wave3_ae_coral.py (all of it: its worm, its egg and halves()) and
wave3_ae_art.py's WORM and EGG (read only by it).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouettes of each whole
and piece against enemy_x27.png, and the worm's containment in the column), --preview <prefix> (each whole: top and
3/4 views; --pieces 1 also each piece's), --only <model,...>, --whole <prefix> (the uncut wholes as
<prefix>worm.glb, <prefix>egg.glb), --stats 1.
"""
import math
import os
import sys

import bpy
import numpy as np
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k  # noqa: E402
from polish_deli_boss import join, drop_unused  # noqa: E402
from polish_orb_red import band_split  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402
import polish_coral_pylon as pylon  # noqa: E402  (the column it lies in: turned surfaces, cut(), its bore)

BOX_T, BOX_B = (-12.0, 12.0, 0.0, 28.0), (-12.0, 12.0, -28.0, 0.0)
WORM_PIECES = [("coral_worm_t", 1, BOX_T), ("coral_worm_b", 39, BOX_B)]
EGG_PIECES = [("coral_egg_t", 14, BOX_T), ("coral_egg_b", 52, BOX_B)]

VIEW_TILT = 20.0             # the game's camera: this far off straight down, from the bottom of the screen
T = math.radians(VIEW_TILT)

# --- The worm ----------------------------------------------------------------------------------------------------------
WORM_Z = 5.0                 # its axis over the floor (its belly about 1.1 over it, on the column's bore floor)
WORM_SQUASH = 0.95
WORM_SEGMENTS = 24
PINCHES = [-18.5, -10.5, -2.5, 5.5, 13.5]     # rows 46, 38, 30, 22, 14
# Its half width along y: the pointed end, the pinches (each segment's rim bulging over its pinch, up the screen of
# it), the neck under the knot.
HEAD = [(-28.0, 0.0), (-27.75, 0.55), (-27.2, 1.25), (-26.3, 2.15), (-25.2, 2.95), (-24.0, 3.55), (-22.8, 3.9),
        (-21.0, 4.05)]
PINCH = [(-1.0, 3.92), (-0.45, 3.78), (0.0, 3.55), (0.4, 3.85), (0.9, 4.08), (1.8, 4.0)]
TAIL = [(20.6, 3.9), (21.8, 3.6), (22.8, 2.7), (23.8, 1.95), (24.7, 1.4), (25.3, 0.0)]
# The knot: lobes (x, y, z over the axis, radii).
KNOT = [((-2.65, 25.9, 0.0), (2.3, 1.8, 2.15)), ((0.0, 25.7, 0.3), (2.1, 1.95, 2.6)),
        ((2.7, 25.9, 0.0), (2.3, 1.8, 2.15))]
# Its shades (ramp 4): by how much a part faces up (as polish_coral_pylon.shade_of), the rims lighter, the pinches
# darker, the glossy highlight over the pointed end (y, spread, lift).
W_UNDER, W_FLANK, W_TOP, W_MID, W_RISE = 3.6, 5.3, 10.4, 0.35, 1.5
RIM_LIFT, RIM_SPREAD, PINCH_DARK, PINCH_SPREAD = 1.0, 0.5, 1.6, 0.3
STRIPE = (0.45, 0.45, 1.9)         # the pale line along its top: x, half width, lift
HEAD_GLOSS = (-21.6, 2.0, 2.6)
WORM_BANDS = [(-99.0, 0x44), (4.5, 0x45), (5.5, 0x46), (6.5, 0x47), (7.5, 0x48), (8.5, 0x49), (9.5, 0x4a),
              (10.5, 0x4b), (11.5, 0x4c), (12.5, 0x4d)]
WORM_FINISH = dict(metallic=0.06, roughness=0.3)
WORM_CUT = 0x46

# --- The egg ----------------------------------------------------------------------------------------------------------
EGG_Y = 1.0                  # its middle (rows 3-50)
EGG_HALF, EGG_W, EGG_H = 24.0, 12.0, 10.5   # half its length, half its width (its ends round of that radius), height
EGG_SEGMENTS = 36            # round its upper half
EGG_LOW = -7.0               # its sides reach this far under the floor (degrees), its bottom closing them
EGG_BLUR = 0.65              # the sprite's shades blurred (pixels)
# (lowest shade, palette index, emission) in the glow; outside it the shades stop at 0x3c and nothing glows.
EGG_BANDS = [(-99.0, 0x34, 0.0), (4.5, 0x35, 0.0), (5.5, 0x36, 0.0), (6.5, 0x37, 0.0), (7.5, 0x38, 0.0),
             (8.5, 0x39, 0.0), (9.5, 0x3a, 0.0), (10.5, 0x3b, 0.0), (11.5, 0x3c, 0.0), (12.5, 0x3d, 0.32),
             (13.3, 0x3e, 0.46), (14.0, 0x6f, 0.6)]   # (the blurred white crescent peaks at 14.37)
GLOW_ZONE = ((-0.5, 0.3), (7.6, 5.2))   # the glow's middle and half sizes in the sprite's picture (x, y)
GLOW_3C = 0.18                          # 0x3c's emission in the glow
EGG_FINISH = dict(metallic=0.15, roughness=0.1)
EGG_CUT = (0x3b, 0.2)          # the cut faces: the egg's inside, glowing faintly


def X(c):
    return c - 11.5


def Y(r):
    return 27.5 - r


# --- Materials ---------------------------------------------------------------------------------------------------------

def worm_materials():
    return {index: k.material(f"worm_{index:02x}", palette=index, **WORM_FINISH) for _, index in WORM_BANDS}


def egg_materials():
    pal = k.level_palette()
    m = {}
    for _, index, glow in EGG_BANDS:
        if glow > 0:
            m[index] = k.material(f"egg_glow_{index:02x}", palette=index, emission=pal[index], emission_strength=glow,
                                  **EGG_FINISH)
        else:
            m[index] = k.material(f"egg_{index:02x}", palette=index, **EGG_FINISH)
    m["3c_glow"] = k.material("egg_glow_3c", palette=0x3c, emission=pal[0x3c], emission_strength=GLOW_3C,
                              **EGG_FINISH)
    index, glow = EGG_CUT
    m["cut"] = k.material(f"egg_inside_{index:02x}", palette=index, emission=pal[index], emission_strength=glow,
                          metallic=0.0, roughness=0.4)
    return m


# --- The worm ----------------------------------------------------------------------------------------------------------

def worm_profile():
    pts = list(HEAD)
    for yp in PINCHES:
        pts += [(yp + dy, w) for dy, w in PINCH]
    pts += TAIL
    return pylon.Monotone(sorted(pts))


def bump(y, centres, spread):
    return sum(math.exp(-((y - c) / spread) ** 2) for c in centres)


def worm_shade(n, co):
    if n.z >= W_MID:
        s = W_FLANK + (W_TOP - W_FLANK) * ((n.z - W_MID) / (1.0 - W_MID)) ** W_RISE
    else:
        s = W_UNDER + (W_FLANK - W_UNDER) * max(0.0, (n.z + 0.35) / (W_MID + 0.35))
    s += RIM_LIFT * bump(co.y, [p + 1.0 for p in PINCHES], RIM_SPREAD) * (0.4 + 0.6 * max(0.0, n.z))
    s -= PINCH_DARK * bump(co.y, PINCHES, PINCH_SPREAD)
    sx, sw, sl = STRIPE
    line = math.exp(-((co.x - sx) / sw) ** 2) * max(0.0, n.z) ** 4
    s += sl * line
    gy, spread, lift = HEAD_GLOSS
    s += lift * math.exp(-((co.y - gy) / spread) ** 2) * line
    return s


def worm_body(m):
    prof = worm_profile()
    obj, _ = pylon.surface_section("worm_body", prof, WORM_SQUASH, prof.x[0], prof.x[-1], True, True, m[0x48],
                                   axis_z=WORM_Z, segments=WORM_SEGMENTS, step=1.0, dr=0.4)
    normal = pylon.turned_normal(prof, WORM_SQUASH, WORM_Z)
    pylon.orient(obj, normal)
    values = [worm_shade(normal(v.co), v.co) for v in obj.data.vertices]
    band_split(obj, values, [(lo, m[index]) for lo, index in WORM_BANDS])
    pylon.orient(obj, normal)
    pylon.set_normals(obj, normal)
    return obj


def worm_knot(m):
    out = []
    for i, ((x, y, dz), radii) in enumerate(KNOT):
        centre = Vector((x, y, WORM_Z + dz))
        obj = mk.ball(f"worm_knot{i}", tuple(centre), radii, m[0x48], 20, 10)

        def normal(co, c=centre, r=radii):
            d = Vector(co) - c
            return Vector((d.x / r[0] ** 2, d.y / r[1] ** 2, d.z / r[2] ** 2)).normalized()
        values = [worm_shade(normal(v.co), Vector((v.co.x, 99.0, v.co.z))) for v in obj.data.vertices]
        band_split(obj, values, [(lo, m[index]) for lo, index in WORM_BANDS])
        pylon.set_normals(obj, normal)
        out.append(obj)
    return out


def build_worm():
    m = worm_materials()
    parts = [worm_body(m)] + worm_knot(m)
    for obj in parts:
        mk.apply(obj)
    triangulate(parts)
    return parts, m


def containment(parts):
    """How far the worm's vertices reach outside the column's outer surface (pixels; <= 0: inside) and how many lie
    outside the bore (sunk into its wall)."""
    worst, in_wall = -99.0, 0
    for obj in parts:
        for v in obj.data.vertices:
            p = obj.matrix_world @ v.co
            r = pylon.R_OUT(p.y)
            if r <= 0.0:
                worst = max(worst, 99.0)
                continue
            q = math.hypot(p.x / r, (p.z - pylon.AXIS_Z) / (r * pylon.SQUASH))
            worst = max(worst, (q - 1.0) * r)
            rb = pylon.R_BORE(p.y)
            if rb <= 0 or math.hypot(p.x / rb, (p.z - pylon.BORE_Z) / (rb * pylon.BORE_SQUASH)) > 1.0:
                in_wall += 1
    return worst, in_wall


# --- The egg ------------------------------------------------------------------------------------------------------------

class EggProfile:
    """The egg's half width along y: straight over its middle, its ends round (pylon.turned_normal's profile)."""

    def __init__(self):
        self.x = [EGG_Y - EGG_HALF, EGG_Y + EGG_HALF]

    def __call__(self, y):
        d = abs(y - EGG_Y) - (EGG_HALF - EGG_W)
        if d <= 0:
            return EGG_W
        return math.sqrt(max(0.0, EGG_W ** 2 - d * d))

    def slope(self, y):
        e = 1e-3
        return (self(y + e) - self(y - e)) / (2 * e)


EGG = EggProfile()
EGG_SQUASH = EGG_H / EGG_W
egg_normal = pylon.turned_normal(EGG, EGG_SQUASH, 0.0)


def egg_ys():
    """The rings' ys: every 0.7 pixels, closer near the ends."""
    ys, y = [], EGG.x[0] + 0.02
    while y < EGG.x[1] - 0.02:
        ys.append(y)
        y += max(0.08, min(0.7, 0.45 / max(abs(EGG.slope(y)), 1e-6)))
    ys.append(EGG.x[1] - 0.02)
    return ys


def egg_shell(m):
    """The egg's upper half (its sides a little under the floor), closed by its bottom; returns the object."""
    ys = egg_ys()
    n = EGG_SEGMENTS
    a0, a1 = math.radians(EGG_LOW), math.pi - math.radians(EGG_LOW)
    verts, faces = [], []
    for y in ys:
        w = EGG(y)
        for j in range(n + 1):
            a = a0 + (a1 - a0) * j / n
            verts.append(Vector((w * math.cos(a), y, EGG_SQUASH * w * math.sin(a))))
    row = n + 1
    for i in range(len(ys) - 1):
        for j in range(n):
            a, b = i * row + j, i * row + j + 1
            faces.append((a, a + row, b + row, b))
        faces.append((i * row + n, (i + 1) * row + n, (i + 1) * row, i * row))   # the bottom
    for end, tip in ((0, EGG.x[0]), (len(ys) - 1, EGG.x[1])):
        verts.append(Vector((0.0, tip, 0.0)))
        c = len(verts) - 1
        faces += [(c, end * row + j, end * row + j + 1) for j in range(n)]
        faces.append((c, end * row + n, end * row))
    obj = k.mesh_object("egg_shell", verts, faces, m[0x38])

    def outward(p):
        if p.z < -0.05 and abs(p.x) < EGG(p.y) * 0.98:
            return Vector((0.0, 0.0, -1.0))
        return egg_normal(p)
    pylon.orient(obj, outward)
    return obj, outward


class SpriteShades:
    """The egg's sprite (14 above 52) as smooth fields over its picture: the shade (ramp 3's, 0x6f as 15) and
    whether a pixel is the egg's, sampled at (x, y) of the picture (y up)."""
    SCALE = 4

    def __init__(self, sheet=None):
        rows = egg_picture(sheet)
        h, w = 56, 24
        s = self.SCALE
        shade, cover = np.zeros((h, w)), np.zeros((h, w))
        for r in range(h):
            for c in range(w):
                v = rows[r][c]
                if v is not None:
                    cover[r, c] = 1.0
                    shade[r, c] = 15.0 if v == 0x6f else float(v & 15)
        up = lambda a: np.kron(a, np.ones((s, s)))  # noqa: E731
        pad = 4 * s
        cov = np.pad(up(cover), pad)
        weight = blur(cov, EGG_BLUR, s)
        self.shade = blur(np.pad(up(shade * cover), pad), EGG_BLUR, s) / np.maximum(weight, 1e-6)
        self.shade[weight < 1e-3] = 6.0
        self.pad = pad

    def sample(self, x, y):
        s = self.SCALE
        fx = (x + 12.0) * s + self.pad - 0.5
        fy = (28.0 - y) * s + self.pad - 0.5
        f = self.shade
        hh, ww = f.shape
        x0, y0 = int(math.floor(fx)), int(math.floor(fy))
        tx, ty = fx - x0, fy - y0
        x0, y0 = max(0, min(ww - 2, x0)), max(0, min(hh - 2, y0))
        a, b, c, d = f[y0, x0], f[y0, x0 + 1], f[y0 + 1, x0], f[y0 + 1, x0 + 1]
        return (a * (1 - tx) + b * tx) * (1 - ty) + (c * (1 - tx) + d * tx) * ty


def blur(a, sigma, scale):
    """A gaussian blur (sigma in pixels) of an array sampled scale times a pixel (polish_coral_eel.py's)."""
    s = sigma * scale
    r = int(math.ceil(3 * s))
    xs = np.arange(-r, r + 1)
    kern = np.exp(-0.5 * (xs / s) ** 2)
    kern /= kern.sum()
    out = np.apply_along_axis(lambda v: np.convolve(np.pad(v, r, mode="edge"), kern, mode="valid"), 0, a)
    return np.apply_along_axis(lambda v: np.convolve(np.pad(v, r, mode="edge"), kern, mode="valid"), 1, out)


# The egg's picture (' 14 above ' 52, rows 0-55), its palette indices (ramp 3 and 0x6f), '.' none: written out so
# that the script needs no sheet; --check compares it with the sheet.
EGG_ROWS = [
    "",
    "",
    "",
    "9:37 37 37 37 37 38",
    "7:37 37 37 37 37 38 38 38 38 38",
    "5:37 37 37 37 37 38 38 38 38 38 38 38 38 38",
    "4:37 37 37 37 38 38 38 38 38 39 39 39 39 38 38 38",
    "3:37 37 37 37 38 38 38 38 38 39 3a 3a 3b 3a 39 38 38 38",
    "2:37 37 37 37 38 38 38 38 38 38 39 3a 3c 3c 3b 39 39 38 38 38",
    "2:37 37 37 38 38 38 38 38 38 38 39 3a 3a 3c 3c 3b 39 39 38 38",
    "1:37 37 37 38 38 39 39 39 38 38 38 39 39 3a 3a 3c 3c 3b 39 39 38 38",
    "1:37 37 37 38 39 39 3a 39 38 38 38 39 39 39 3a 3a 3c 3b 3b 39 39 38",
    "0:37 37 37 39 39 39 3a 39 39 38 38 38 38 39 39 39 3a 3a 3c 3b 3b 39 38 38",
    "0:37 37 38 39 3a 3a 39 39 38 38 38 38 38 38 39 39 39 3a 3c 3c 3b 39 39 38",
    "0:37 38 39 39 3a 39 39 38 38 39 38 39 39 39 39 39 39 3a 3a 3c 3b 3b 39 38",
    "0:37 38 39 3a 3a 39 38 39 39 39 39 39 3a 3a 39 39 39 39 3a 3a 3c 3b 39 39",
    "0:38 39 39 3a 39 39 38 39 39 39 39 38 39 3a 3a 39 39 39 39 3a 3c 3b 3b 39",
    "0:38 39 39 3a 39 38 38 39 39 3a 39 38 39 39 3a 39 39 39 39 39 3a 3a 39 39",
    "0:38 39 39 39 39 38 39 39 3a 3a 39 39 38 39 39 3a 39 38 39 39 3a 39 39 38",
    "0:38 38 39 39 38 38 39 39 3a 3a 39 39 38 38 39 39 39 38 39 39 39 39 39 38",
    "0:38 38 38 39 38 38 39 39 3a 3a 39 39 39 38 38 38 38 38 39 39 39 39 38 38",
    "0:38 38 38 38 38 38 39 39 3a 3a 3a 39 39 39 38 38 38 38 38 39 39 39 38 38",
    "0:38 38 38 38 38 39 39 39 39 3a 3b 3a 39 39 39 39 39 38 38 38 39 38 38 38",
    "0:38 38 38 38 39 39 39 39 3a 3a 3b 3b 39 3a 3a 3a 39 39 38 38 38 38 38 38",
    "0:38 38 38 38 39 39 3a 3a 3a 3c 3c 3b 3a 3a 3c 3a 3a 39 39 38 38 38 38 38",
    "0:38 38 38 39 39 3a 3a 3c 3c 3d 3d 3c 3c 3c 3d 3c 3a 3a 39 39 38 38 38 38",
    "0:38 38 38 39 3a 3a 3c 3c 3d 3e 3d 3d 3c 3d 3e 3d 3c 3a 3a 39 38 38 38 38",
    "0:38 38 38 39 3a 3b 3c 3d 3e 6f 3d 3d 3d 3d 6f 3e 3d 3c 3a 39 38 38 38 38",
    "0:38 38 39 39 3a 3b 3c 3d 3d 3e 6f 6f 6f 6f 3e 3d 3d 3c 3a 39 38 38 38 38",
    "0:38 38 39 39 3a 3b 3c 3c 3d 3d 3e 3e 3e 3e 3d 3c 3c 3a 3a 39 38 38 38 38",
    "0:38 39 39 39 3a 3a 3b 3c 3c 3d 3d 3d 3d 3d 3c 3a 3a 3a 39 39 38 38 38 38",
    "0:38 39 39 39 39 3a 3b 3b 3c 3c 3c 3c 3c 3c 3a 3a 3a 39 39 38 38 38 38 38",
    "0:38 38 39 39 39 3a 3a 3b 3b 3c 3c 3c 3c 3a 3a 3a 39 39 38 38 38 38 38 37",
    "0:37 38 39 39 39 39 3a 3a 3b 3b 3b 3b 3a 3a 39 39 39 38 38 38 38 38 38 37",
    "0:37 38 38 39 39 39 39 3a 3a 3a 3b 3b 3a 39 39 39 38 38 38 38 38 38 38 37",
    "0:37 38 38 39 39 39 39 39 3a 3a 3a 3a 39 39 38 38 38 38 38 38 38 38 38 37",
    "0:37 38 38 38 39 39 39 39 39 39 39 3a 3a 39 39 38 38 38 38 38 38 38 38 37",
    "0:37 37 38 38 38 39 39 39 39 39 39 39 39 39 39 38 38 38 38 38 38 38 37 37",
    "0:37 37 37 38 38 38 39 39 39 39 39 39 39 39 39 38 38 38 38 38 38 38 37 37",
    "0:37 37 37 38 38 38 38 38 39 39 39 39 39 39 39 38 38 38 38 38 38 37 37 37",
    "0:36 37 37 37 38 38 38 38 38 39 39 39 39 39 39 39 38 38 38 38 38 37 37 36",
    "0:34 37 37 37 38 38 38 38 38 38 38 39 39 39 39 39 39 38 38 38 37 37 37 35",
    "1:36 37 37 37 38 38 38 38 38 38 38 38 39 39 39 38 38 38 37 37 37 37",
    "1:35 37 37 37 37 38 38 38 38 38 38 38 38 38 38 38 38 37 37 37 37 35",
    "2:36 37 37 37 37 38 38 38 38 38 38 38 38 38 38 38 37 37 37 37",
    "2:35 37 37 37 37 37 38 38 38 38 38 38 38 38 38 37 37 37 37 35",
    "3:36 37 37 37 37 37 37 38 38 38 38 38 38 37 37 37 37 35",
    "4:36 37 37 37 37 37 37 38 38 38 38 37 37 37 37 35",
    "5:35 36 37 37 37 37 37 37 37 37 37 37 37 35",
    "7:35 36 37 37 37 37 37 37 37 35",
    "9:35 36 36 36 36 35",
    "",
    "",
    "",
    "",
    "",
]


def egg_picture(sheet=None):
    """The egg's 24 x 56 picture: rows of palette indices (None: transparent), from EGG_ROWS or the sheet."""
    if sheet:
        from sprite_profile import sprite_indices
        rows = []
        for sprite in (14, 52):
            rows += [list(r) for r in sprite_indices(sheet, sprite, True)]
        return rows
    rows = []
    for text in EGG_ROWS:
        row = [None] * 24
        if text:
            start, _, values = text.partition(":")
            for i, v in enumerate(values.split()):
                row[int(start) + i] = int(v, 16)
        rows.append(row)
    return rows


def paint_egg(obj, outward, m, shades):
    """The egg's shell in the sprite's shades where the game's camera sees each point, banded."""
    (gx, gy), (rx, ry) = GLOW_ZONE
    tan = math.tan(T)
    mesh = obj.data
    values, glow = [], []
    for v in mesh.vertices:
        p = v.co
        sx, sy = p.x, p.y + max(0.0, p.z) * tan
        s = shades.sample(sx, sy)
        inside = ((sx - gx) / rx) ** 2 + ((sy - gy) / ry) ** 2 < 1.0
        if not inside:
            s = min(s, 12.45)
        values.append(s)
        glow.append(inside)
    band_split(obj, values, [(lo, m[index]) for lo, index, _ in EGG_BANDS])
    # 0x3c glows where it is the glow's (inside the zone), not in the reflected streak.
    mesh = obj.data
    slot = mk.slot_of(obj, m["3c_glow"])
    plain = [i for i, mat in enumerate(mesh.materials) if mat == m[0x3c]]
    for poly in mesh.polygons:
        if poly.material_index in plain:
            c = poly.center
            sx, sy = c.x, c.y + max(0.0, c.z) * tan
            if ((sx - gx) / rx) ** 2 + ((sy - gy) / ry) ** 2 < 1.0:
                poly.material_index = slot
    pylon.orient(obj, outward)

    def normal(co):
        if co.z < -0.05 and abs(co.x) < EGG(co.y) * 0.98:
            return Vector((0.0, 0.0, -1.0))
        return egg_normal(co)
    pylon.set_normals(obj, normal)
    # The bottom (under the floor) flat.
    return obj


def build_egg(sheet=None):
    m = egg_materials()
    shell, outward = egg_shell(m)
    paint_egg(shell, outward, m, SpriteShades(sheet))
    mk.apply(shell)
    triangulate([shell])
    return [shell], m


# --- Checks, export ------------------------------------------------------------------------------------------------------

def whole_mask(sheet, sprites):
    mask = []
    for sprite in sprites:
        mask += k.sprite_mask(sheet, sprite)
    return mask


def export_whole(label, parts, m, pieces, cap, options, sheet, out, size=(24, 56)):
    only = options["only"].split(",") if "only" in options else None
    wanted = [p for p in pieces if not only or p[0] in only]
    low, high = mk.bounds(parts)
    print("== whole %s: %d triangles, %d materials, x %.2f..%.2f y %.2f..%.2f z %.2f..%.2f" % (
        label, mk.triangles(parts), len(mk.materials_of(parts)), low.x, high.x, low.y, high.y, low.z, high.z))
    if sheet:
        mk.compare("whole %s (x27 %d above %d)" % (label, pieces[0][1], pieces[1][1]), mk.coverage(parts, *size),
                   whole_mask(sheet, [p[1] for p in pieces]))
    bpy.context.scene.view_settings.view_transform = "Standard"
    if "preview" in options:
        mk.preview(options["preview"] + "coral_%s_whole" % label, parts, size=size, scale=12, distance=1.6)
    if "whole" in options:
        mk.export(parts, options["whole"] + label + ".glb")
    for name, sprite, box in wanted:
        cut_parts = [p for p in (pylon.cut(src, box, cap) for src in parts) if p is not None]
        drop_unused(cut_parts)
        mk.transform(cut_parts, Matrix.Translation((-(box[0] + box[1]) / 2, -(box[2] + box[3]) / 2, 0)))
        bpy.context.view_layer.update()
        triangulate(cut_parts)
        obj = join(cut_parts, name)
        obj.data.name = name
        obj.hide_render = False
        for src in parts:
            src.hide_render = True
        if sheet:
            mk.compare("%s (x27 %d)" % (name, sprite), mk.coverage([obj], 24, 28), k.sprite_mask(sheet, sprite))
        mk.report(name, [obj], os.path.join(out, name + ".glb"))
        if "preview" in options and options.get("pieces") == "1":
            mk.preview(options["preview"] + name, [obj])
        bpy.data.objects.remove(obj)
        for src in parts:
            src.hide_render = False


def build():
    options = k.args()
    out = mk.outdir(options)
    only = options["only"].split(",") if "only" in options else None
    sheet = None
    if "check" in options:
        sheets = options["check"]
        sheet = os.path.join(sheets, "enemy_x27.png") if os.path.isdir(sheets) else sheets
    if not only or any(n in only for n, _, _ in WORM_PIECES):
        k.reset()
        parts, m = build_worm()
        if sheet:
            worst, in_wall = containment(parts)
            print("worm in the column: reaches %.3f px past its outer surface (<= 0: inside); %d vertices in the "
                  "bore's wall" % (worst, in_wall))
        export_whole("worm", parts, m, WORM_PIECES, m[WORM_CUT], options, sheet, out)
    if not only or any(n in only for n, _, _ in EGG_PIECES):
        k.reset()
        if sheet:
            drawn, written = egg_picture(sheet), egg_picture()
            print("egg picture as written matches the sheet: %s" % (drawn == written))
        parts, m = build_egg()
        export_whole("egg", parts, m, EGG_PIECES, m["cut"], options, sheet, out)


if __name__ == "__main__":
    build()
