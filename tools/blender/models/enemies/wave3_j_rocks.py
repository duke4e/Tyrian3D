"""Enemies of wave 3, batch J (sheet D, the asteroid levels), the rocks and the stone face; modelled as
their sprites look (models.cfg: yaw=0). The machines are in wave3_j.py; the two big asteroids (D 1 3 / 39 41 and
D 7 9 / 45 47) in polish_asteroids.py; the small rocks (D 95, 114, 133, 152) in polish_pebbles.py.

- crag_* (D 13, 15, 31, 34, 49, 51, 53, 88, 89, 91): the huge asteroid of ASTEROID1 and ASTEROIDS,
  72 x 84 pixels, which the game puts together from ten sprites (six 2x2, four 1x1), built whole
  the same way and cut into the ten pieces (origin).
- rock_a, rock_b, rock_c (D 43, 85, 123): asteroids floating in the sky, faceted like D 5's
  (asteroid_lumpy, now polish_asteroid_lumpy.py).
- rock_beacon (D 93): such an asteroid with a red beacon on its side (its frames 55 and 18 light
  the beacon: it glows).
- rock_blue_eye (D 229): such an asteroid with a blue light set in its middle (its frames 231-235
  light it up: it glows).
- stone_face_tl, stone_face_tr, stone_face_bl, stone_face_br (D 155, P 123, D 165, P 127): the stone
  face lying on the ground of ASTEROID1 and ASTEROID2, which the game puts together from two
  sprites of sheet D and two of sheet P (event 12), built whole and cut (origin).

usage: Blender -b --factory-startup -P wave3_j_rocks.py -- [--only name,name] [--preview <prefix>]
       [--check <directory of the extracted sheets>] [--stats 1]
       [--whole crag|stone_face --preview <prefix>]
"""
import math
import os
import sys

from mathutils import Matrix, Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_j_kit as w  # noqa: E402
from wave3_j_kit import art, k, sh, pal, model, whole  # noqa: E402

D = "enemy_D"
P = "enemy_P"


# --- Boulder clusters on the ground --------------------------------------------------------------

def cluster(g, origin, boulders, prefix, seed=11, height_scale=1.0, size_scale=1.0):
    """A big asteroid on the ground: lumpy grey boulders where the
    sprite draws its lobes, packed on a low dark base that fills the cracks between them. boulders:
    ((column, row), (rx, ry), height, turn) in the art's pixels; each boulder's shade follows the
    sprite's mean shade round its centre."""
    ox, oy = origin
    rows = w.regions(g, lambda v, c, r: "#")
    base = pal(f"{prefix}_base", 6, metallic=0.05, roughness=0.8)
    polys = sh.outlines(rows, "#", origin, smooth=2, epsilon=0.6, min_area=4.0)
    outline = max(polys, key=len)
    k.smooth(sh.inflate("base", [sh.inset(p, 0.8) for p in polys], base, sh.round_profile(0.5, max_height=2.6),
                        bottom=0.0, spacing=0.9, sigma=2.0), 60)
    shade = w.sampler(g, origin, value=lambda v: v & 15 if v >> 4 == 0 else 7, blur=2,
                      keep=lambda v: v is not None and v != 0x20)
    for i, ((c, r), (rx, ry), h, turn) in enumerate(boulders):
        x, y = c + 0.5 - ox, oy - (r + 0.5)
        s = shade(x, y)
        index = max(7, min(11, int(round(4.5 + 0.55 * s))))
        mat = pal(f"{prefix}_rock{index}", index, metallic=0.05, roughness=0.75)
        h *= height_scale
        rx, ry = rx * size_scale, ry * size_scale
        rock = w.lumpy(f"boulder{i}", (0, 0, 0), (rx * 1.08, ry * 1.08, h * 0.85), mat, seed=seed + i, amount=0.2,
                       segments=14, rings=9, smooth_angle=32)
        rock.data.transform(Matrix.Translation((x, y, -0.1 * h)) @ Matrix.Rotation(math.radians(turn), 4, "Z"))
        clamp_to_outline(rock, outline, (x, y))
    sh.flat_bottom(w.meshes())


def clamp_to_outline(obj, poly, centre):
    """Pulls the vertices of a part that stick out of the outline back onto it, along rays from
    `centre` (the top view keeps the sprite's outline)."""
    cx, cy = centre
    for v in obj.data.vertices:
        dx, dy = v.co.x - cx, v.co.y - cy
        d = math.hypot(dx, dy)
        if d < 1e-6:
            continue
        limit = w._ray_polygon(poly, (cx, cy), (dx / d, dy / d))
        if limit > 0 and d > limit:
            v.co.x, v.co.y = cx + dx * limit / d, cy + dy * limit / d


# --- D 13, 15, 31, 34, 49, 51, 53, 88, 89, 91: the huge asteroid ---------------------------------

CRAG_BOULDERS = [
    ((34.0, 12.0), (7.0, 7.0), 11.0, 10), ((45.0, 15.5), (5.0, 7.0), 9.0, -10), ((24.5, 22.0), (6.0, 6.0), 9.0, 20),
    ((32.5, 30.0), (9.0, 7.2), 12.5, 0), ((43.5, 30.0), (5.2, 6.2), 10.0, 15), ((19.5, 32.5), (6.0, 6.0), 9.0, -25),
    ((12.0, 41.0), (8.0, 6.0), 9.5, 5), ((24.5, 45.0), (7.0, 7.0), 11.0, -10), ((38.0, 47.5), (7.0, 7.0), 11.5, 20),
    ((55.0, 48.0), (6.0, 7.0), 10.5, -5), ((52.0, 35.5), (6.0, 7.0), 10.0, 10), ((20.0, 58.0), (8.0, 7.0), 10.0, 0),
    ((34.0, 62.0), (8.0, 7.0), 11.0, -15), ((55.0, 65.0), (6.0, 6.0), 9.5, 25), ((28.5, 71.5), (7.5, 5.0), 8.0, 0),
    ((46.0, 70.0), (7.0, 6.0), 9.0, -10), ((61.0, 57.0), (4.0, 8.0), 8.0, 0), ((13.5, 55.0), (5.0, 6.0), 7.5, 15),
    ((45.0, 58.5), (5.0, 5.0), 9.5, 0), ((8.0, 34.0), (3.5, 4.0), 6.5, 0), ((54.5, 23.5), (5.0, 6.5), 9.0, 15),
    ((63.0, 42.0), (4.0, 6.5), 8.0, -10), ((62.5, 68.0), (5.0, 6.0), 8.0, 10), ((53.0, 75.0), (6.0, 3.2), 6.5, 0),
    ((40.0, 76.0), (5.0, 2.8), 6.0, 0), ((60.0, 33.0), (3.5, 4.5), 7.0, 0), ((16.0, 66.0), (5.0, 3.5), 6.5, 0),
    ((29.0, 6.5), (4.0, 3.0), 7.0, 0), ((39.5, 6.5), (4.0, 3.0), 7.0, 0),
]
# The pieces: name, sprite, large, left and top in the art's pixels (the art is the sheet's columns 10-15
# and rows 0-5, 72 x 84 pixels).
CRAG_PIECES = [
    ("crag_13", 13, True, 24, 0), ("crag_15", 15, False, 48, 0), ("crag_31", 31, False, 12, 14),
    ("crag_34", 34, False, 48, 14), ("crag_49", 49, True, 0, 28), ("crag_51", 51, True, 24, 28),
    ("crag_53", 53, True, 48, 28), ("crag_88", 88, False, 12, 56), ("crag_89", 89, True, 24, 56),
    ("crag_91", 91, True, 48, 56),
]


@whole("crag", (72, 84))
def crag_whole():
    g = w.grid(art.HUGE, 72)
    for r in range(28):  # the bronze beetle (D 16) beside it on the sheet
        for c in range(60, 72):
            g[r][c] = None
    cluster(g, (36, 42), CRAG_BOULDERS, "crag", seed=51, height_scale=1.1, size_scale=1.1)


def crag_piece(large, left, top):
    crag_whole()
    w.bake()
    pw, ph = (24, 28) if large else (12, 14)
    x0, y1 = left - 36, 42 - top
    w.piece(w.meshes(), x0, x0 + pw, y1 - ph, y1)


for _name, _sprite, _large, _left, _top in CRAG_PIECES:
    model(_name, [(D, _sprite, _large)], size=(24, 28) if _large else (12, 14))(
        lambda large=_large, left=_left, top=_top: crag_piece(large, left, top))


# --- Asteroids in the sky (D 43, 85, 123, 93, 229) ------------------------------------------------

def sky_rock(g, prefix, seed, height=6.6, depth=None):
    """A faceted grey asteroid over the sprite's outline (as asteroid_lumpy)."""
    shades = [pal(f"{prefix}_{i:x}", i, metallic=0.1, roughness=0.75) for i in range(0x04, 0x0d)]
    rows = w.regions(g, lambda v, c, r: "#")
    poly = max(sh.outlines(rows, "#", (12, 14), smooth=2, epsilon=0.3), key=len)
    shade = w.sampler(g, (12, 14), value=lambda v: v & 15 if v >> 4 == 0 else 8, blur=1,
                      keep=lambda v: v is not None and v != 0x20)

    def shade_of(c, n):
        # The sprite's shade where the facet lies, a little lighter facing the sun.
        s = shade(c.x, c.y) - 4.0 + 1.5 * (-0.45 * n.x + 0.35 * n.y + 0.8 * n.z)
        return s if n.z > -0.2 else 0.5
    return w.faceted_rock("rock", poly, height, shades, seed=seed, depth=depth, shade_of=shade_of)


@model("rock_a", [(D, 43, True)])
def rock_a():
    """A faceted grey asteroid (D 43)."""
    sky_rock(w.grid(art.D43, 24), "rock_a", 7, height=6.4)


@model("rock_b", [(D, 85, True)])
def rock_b():
    """A faceted grey asteroid (D 85)."""
    sky_rock(w.grid(art.D85, 24), "rock_b", 13, height=7.0)


@model("rock_c", [(D, 123, True)])
def rock_c():
    """A faceted grey asteroid (D 123)."""
    sky_rock(w.grid(art.D123, 24), "rock_c", 21, height=6.8)


@model("rock_beacon", [(D, 93, True)])
def rock_beacon():
    """A faceted asteroid with a red beacon on its right side: a steel housing round a glowing lamp
    (frames 55 and 18 light it)."""
    rock = sky_rock(w.grid(art.D93, 24), "rock_beacon", 17, height=6.6)
    steel = pal("beacon_steel", 0x66, metallic=0.7, roughness=0.3)
    lamp = pal("beacon_lamp", 0x77, metallic=0.0, roughness=0.3, glow=1.4)
    x, y = w.px(19.0), w.py(12.0)
    z = sh.surface_z(rock, x, y, 4.0)
    w.rounded_box("beacon_housing", (x, y, z - 0.2), (3.8, 5.6, 2.6), steel, bevel=0.6)
    w.sphere("beacon_lamp", (x, y, z + 0.9), (1.5, 2.3, 1.2), lamp, 16, 8)


@model("rock_blue_eye", [(D, 229, True)])
def rock_blue_eye():
    """A faceted asteroid with a blue light set in its middle (frames 231-235 light it)."""
    rock = sky_rock(w.grid(art.D229, 24), "rock_blue_eye", 29, height=6.6)
    blue = pal("blue_eye", 0x9c, metallic=0.1, roughness=0.15, glow=1.2)
    rim = pal("blue_eye_rim", 0x99, metallic=0.4, roughness=0.3)
    x, y = w.px(12.0), w.py(14.0)
    z = sh.surface_z(rock, x, y, 5.0)
    w.lathe_axis("eye_rim", [(-1.0, 2.4), (0.2, 2.4), (0.5, 1.9), (0.55, 1.4)], rim, (x, y, z - 0.3), (0, 0, 1), 16,
                 up=(0, 1, 0))
    w.sphere("eye", (x, y, z + 0.1), (1.6, 1.6, 1.0), blue, 16, 8)
    # Four short rays (the sprite's cross of light).
    for a in range(4):
        d = Vector((math.cos(a * math.pi / 2), math.sin(a * math.pi / 2), 0))
        w.sphere(f"ray{a}", (x + d.x * 2.0, y + d.y * 2.0, z + 0.05), (0.7 + 0.5 * abs(d.x), 0.7 + 0.5 * abs(d.y), 0.5),
                 blue, 10, 5)


# --- D 155, P 123, D 165, P 127: the stone face ---------------------------------------------------

def gauss(x, y, cx, cy, sx, sy):
    return math.exp(-(((x - cx) / sx) ** 2 + ((y - cy) / sy) ** 2))


@whole("stone_face", (48, 56))
def stone_face_whole():
    """A grey stone face lying on the ground, its forehead up the screen: an oval head, a high
    forehead, a heavy brow over two deep eye sockets, a long nose, cheekbones, a mouth with full
    lips and a round chin; painted in the sprite's shades (the sockets and the mouth dark)."""
    g = w.grid(art.FACE, 48)
    origin = (24, 28)
    x0 = 2.6  # the face's middle
    rows = w.regions(g, lambda v, c, r: "#")
    polys = sh.outlines(rows, "#", origin, smooth=2, epsilon=0.4, min_area=4.0)

    def features(x, y, z):
        u = x - x0
        z += 1.2 * gauss(x, y, x0, 13.0, 8.0, 6.0)                                     # the forehead
        z += 2.6 * gauss(u * 0.8, y, 0.0, 6.6, 10.5, 1.5)                              # the brow
        for ex in (-6.4, 6.4):                                                         # the eye sockets
            z -= 4.2 * gauss(u, y, ex, 2.7, 3.9, 2.5)
            z += 1.4 * gauss(u, y, ex, 2.3, 1.8, 1.1)                                  # the eyeballs
        t = min(1.0, max(0.0, (5.0 - y) / 10.0))                                       # the nose, rising
        z += (1.5 + 3.8 * t) * gauss(u, y, 0.3, -0.4, 1.35 + 0.5 * t, 5.2)
        z += 1.6 * gauss(u, y, 0.3, -5.0, 2.3, 1.2)                                    # the nostrils
        for cx in (-7.6, 7.6):                                                         # the cheekbones
            z += 1.8 * gauss(u, y, cx, -3.2, 3.2, 2.6)
            z -= 1.2 * gauss(u, y, cx * 0.8, -8.5, 2.5, 3.0)                           # hollow cheeks
        z -= 2.0 * gauss(u, y, 0.3, -8.0, 4.6, 0.5)                                    # the mouth
        z += 1.3 * gauss(u, y, 0.3, -6.9, 4.0, 0.7)                                    # the upper lip
        z += 1.7 * gauss(u, y, 0.3, -10.0, 3.6, 1.1)                                   # the lower lip
        z += 2.2 * gauss(u, y, 0.3, -16.3, 4.0, 2.8)                                   # the chin
        return z

    stone = pal("face_stone", 0x07, metallic=0.05, roughness=0.7)
    face = sh.inflate("face", polys, stone, sh.pillow_profile(5.5, 6.0, crown=1.5), bottom=0.0, spacing=0.45,
                      z_fn=features, sigma=2.5)
    w.simplify_bottom(face)
    w.decimate(face, 4200)
    k.smooth(face, 70)
    dark = pal("face_dark", 0x04, metallic=0.05, roughness=0.8)
    deep = pal("face_deep", 0x02, metallic=0.05, roughness=0.85)

    def paint(c, n):
        # The hollows (the sockets, the mouth) darker, as the sprite draws them; the rest stone.
        dent = features(c.x, c.y, 0.0)
        return deep if dent < -2.4 else dark if dent < -0.8 else None
    w.paint_faces(face, paint)


def stone_face_piece(x0, x1, y0, y1):
    stone_face_whole()
    w.bake()
    w.piece(w.meshes(), x0, x1, y0, y1)


model("stone_face_tl", [(D, 155, True)])(lambda: stone_face_piece(-24, 0, 0, 28))
model("stone_face_tr", [(P, 123, True)])(lambda: stone_face_piece(0, 24, 0, 28))
model("stone_face_bl", [(D, 165, True)])(lambda: stone_face_piece(-24, 0, -28, 0))
model("stone_face_br", [(P, 127, True)])(lambda: stone_face_piece(0, 24, -28, 0))


w.run()
