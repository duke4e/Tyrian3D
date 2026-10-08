"""Enemies of wave 3, batch M (sheet J), the big green shell of ?TUNNEL? (on the ground) and of TORM,
BOTANY A and BOTANY B (on the top layer); modelled as its sprites look (models.cfg: yaw=0). The other
models of sheet J are in wave3_m.py and wave3_m_ground.py.

- green_shell_153 ... green_shell_271: the shell, 96 x 112 pixels, which the level events put
  together from fifteen 2x2 sprites: 153, 155, 157, 159 / 191, 193, 195, 197 / 229, 241, 243, 235
  and, 12 pixels to the right, 267, 269, 271 (?TUNNEL? event at time 200; 193, 195, 241 and 243
  are enemies 772-775, placed by their own events). A ribbed green carapace narrowing to two
  lobes at the bottom; on it two grey pistons and a grey yoke over its top, a twin glass dome with
  a spine between its halves (its frames light the dome green: it glows faintly), grey shoulder
  plates at both sides, a cross of struts and a stalk down to a housing with a green eye half
  hidden under two lids (241 and 243: the frames open it), a dark grille below and two green
  lamps on the lobes. Built whole and cut into its fifteen pieces (origin).

usage: Blender -b --factory-startup -P wave3_m_shell.py -- [--only name,name] [--preview <prefix>]
       [--check <directory of the extracted sheets>] [--stats 1] [--whole shell --preview <prefix>]
"""
import math
import os
import sys

from mathutils import Matrix, Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave3_m_kit as w  # noqa: E402
from wave3_m_kit import art, k, sh, pal, model, whole, J  # noqa: E402

ORIGIN = (48, 56)
RIB = 5.2  # the ribs' spacing


def X(col):
    return col + 0.5 - ORIGIN[0]


def Y(row):
    return ORIGIN[1] - (row + 0.5)


def materials():
    lp = k.level_palette()
    return {
        "g_dark": pal("shell_green2", 0x22, metallic=0.35, roughness=0.45),
        "g_deep": pal("shell_green4", 0x24, metallic=0.4, roughness=0.4),
        "green": pal("shell_green6", 0x26, metallic=0.45, roughness=0.35),
        "g_light": pal("shell_green8", 0x28, metallic=0.45, roughness=0.3),
        "g_pale": pal("shell_greena", 0x2a, metallic=0.4, roughness=0.28),
        "black": pal("shell_black", 0x01, metallic=0.4, roughness=0.55),
        "grey3": pal("shell_grey3", 0x03, metallic=0.6, roughness=0.4),
        "grey5": pal("shell_grey5", 0x05, metallic=0.65, roughness=0.35),
        "grey7": pal("shell_grey7", 0x07, metallic=0.65, roughness=0.3),
        "grey9": pal("shell_grey9", 0x09, metallic=0.65, roughness=0.28),
        "greyb": pal("shell_greyb", 0x0b, metallic=0.65, roughness=0.25),
        "greyd": pal("shell_greyd", 0x0d, metallic=0.6, roughness=0.22),
        "glass": pal("shell_dome", 0x08, metallic=0.5, roughness=0.06, glow=0.2, emission=lp[0xc5]),
        "glass_hi": pal("shell_dome_hi", 0x0e, metallic=0.2, roughness=0.05),
        "eye": pal("shell_eye", 0xc8, metallic=0.1, roughness=0.1, glow=1.2),
        "eye_core": pal("shell_eye_core", 0xcd, metallic=0.0, roughness=0.05, glow=1.8),
        "lamp": pal("shell_lamp", 0xc6, metallic=0.1, roughness=0.15, glow=1.1),
    }


def rib_phase(x):
    return math.cos(2 * math.pi * (x - 0.6) / RIB)


@whole("shell", (96, 112))
def shell_whole():
    g = w.grid(art.BOSS, 96)
    m = materials()
    # The carapace: the whole outline, rounded over its edge and bulging in the middle, ribbed.
    rows = w.regions(g, lambda v, c, r: "#")
    polys = sh.outlines(rows, "#", ORIGIN, smooth=2, epsilon=0.5, min_area=2.0)

    def ribs(x, y, z):
        fade = min(1.0, max(0.0, (z - 1.5) / 2.5))
        return z - 0.75 * fade * (0.5 + 0.5 * rib_phase(x))
    shell = sh.inflate("carapace", polys, m["green"], sh.pillow_profile(5.5, 10.0, crown=11.0), bottom=0.0, spacing=0.9,
                       z_fn=ribs, sigma=2.0)
    w.simplify_bottom(shell)
    k.smooth(shell, 60)

    def paint(c, n):
        if n.z < 0.35:
            return m["g_dark"] if n.y < 0.0 else m["g_deep"]
        p = rib_phase(c.x)
        if p > 0.8:
            return m["g_deep"]
        if p < -0.75:
            return m["g_pale"] if n.z > 0.95 and c.y > 18.0 else m["g_light"]
        return None
    w.paint_faces(shell, paint)

    def top(x, y, default=6.0):
        return sh.surface_z(shell, x, y, default)

    # The pistons at the upper sides, grey bars from them in to the dome.
    for x in (X(12.0), X(83.0)):
        z = top(x, Y(19.0))
        w.lathe_axis(f"piston{x:.0f}", k.profile([(0.0, 0.01), (0.6, 2.4), (1.6, 3.1), (11.5, 3.1), (13.0, 2.8), (14.4, 0.01)],
                                                 0.6), m["grey7"], (x, Y(12.0), z + 1.0), (0, -1, -0.06), 20)
        w.lathe_axis(f"piston_ring{x:.0f}", [(5.6, 3.1), (5.8, 3.5), (6.8, 3.5), (7.0, 3.1)], m["grey3"],
                     (x, Y(12.0), z + 1.0), (0, -1, -0.06), 20)
        inner = X(30.0) if x < 0 else X(65.0)
        w.tube(f"bar{x:.0f}", [(x, Y(20.5), z + 1.6), ((x + inner) / 2, Y(20.5), top((x + inner) / 2, Y(20.5)) + 1.2),
                               (inner, Y(20.5), top(inner, Y(20.5)) + 0.8)], 1.7, m["grey5"], 12, squash=0.85)
    # The dome: two glass lobes either side of a spine running down from the carapace's top edge, a
    # grey cowl under them.
    dome_z = top(0.0, Y(30.0)) - 4.0
    w.sphere("cowl", (0.0, Y(39.0), dome_z), (15.5, 8.4, 8.6), m["grey5"], 36, 14)
    for x, s in ((X(38.5), -1), (X(56.5), 1)):
        w.sphere(f"dome{s}", (x, Y(28.0), dome_z), (10.4, 11.4, 11.0), m["glass"], 36, 18)
        w.sphere(f"dome_glint{s}", (x - 3.6, Y(28.0) + 4.2, dome_z + 9.6), (2.2, 1.6, 0.5), m["glass_hi"], 12, 6)
    spine = [(0.0, Y(3.0), top(0.0, Y(3.0)) + 0.4), (0.0, Y(10.0), top(0.0, Y(10.0)) + 1.2),
             (0.0, Y(17.0), dome_z + 9.4), (0.0, Y(26.0), dome_z + 11.2), (0.0, Y(35.0), dome_z + 9.0),
             (0.0, Y(41.0), dome_z + 6.0)]
    w.tube("spine", w.catmull(spine, 1.0), 1.8, m["grey7"], 12, squash=1.1)
    for i, yy in enumerate((Y(14.0), Y(20.0), Y(26.0), Y(32.0))):
        zz = dome_z + (8.8, 10.6, 11.4, 10.4)[i]
        w.rounded_box(f"spine_plate{i}", (0.0, yy, zz + 1.6), (3.6, 2.6, 1.2), m["greyb"], bevel=0.35)
    # The shoulder plates at both sides, pointed at their lower ends.
    left = [(X(21.5), Y(55.0)), (X(21.5), Y(39.0))]
    for i in range(1, 12):
        a = math.radians(180 * i / 12)
        left.append((X(14.0) + 7.5 * math.cos(a), Y(39.0) + 4.0 * math.sin(a)))
    left += [(X(6.5), Y(39.0)), (X(7.5), Y(58.0)), (X(11.5), Y(65.5)), (X(17.0), Y(64.0))]
    right = [(-x, y) for x, y in reversed(left)]
    for s, poly in ((-1, left), (1, right)):
        cx = sum(x for x, _ in poly) / len(poly)
        half = 7.5
        base = top(cx, Y(45.0)) - 2.5
        plate = sh.inflate(f"shoulder{s}", [poly], m["grey9"], sh.pillow_profile(3.4, 3.0, crown=1.6), base=base,
                           bottom=0.0, spacing=0.6, sigma=1.4)
        w.decimate(plate, 1600)
        k.smooth(plate, 45)
        w.paint_faces(plate, lambda c, n: m["grey3"] if n.z < 0.3 else None)
        # A light bevel down its inner edge.
        xi = cx - s * (half - 1.2)
        w.tube(f"shoulder_edge{s}", [(xi, Y(38.0), base + 4.4), (xi, Y(52.0), base + 4.6),
                                     (cx - s * 1.0, Y(62.5), base + 3.6)], 0.6, m["greyd"], 8)
    # Under the dome: a housing with a cross of struts on it, green lamps beside it, a stalk down to
    # the eye's ring.
    hz = top(0.0, Y(52.0)) - 3.0
    housing = w.block("housing", (0.0, Y(52.0)), 8.6, 5.6, 4.8, m["grey5"], taper=0.8, rounding=1.6, power=3.0,
                      segments=36, z0=hz)
    w.paint_faces(housing, lambda c, n: m["grey9"] if n.z > 0.85 else m["grey3"] if n.y < -0.4 else None)
    for a, b in (((-6.5, Y(48.5)), (6.5, Y(55.5))), ((6.5, Y(48.5)), (-6.5, Y(55.5)))):
        w.tube(f"strut{a[0]:.0f}", [(a[0], a[1], hz + 5.0), (b[0], b[1], hz + 4.8)], 1.3, m["greyb"], 10)
    w.sphere("cross_hub", (0.0, Y(52.0), hz + 5.4), (2.4, 2.0, 1.4), m["grey9"], 16, 8)
    for x, y in ((X(33.5), Y(53.5)), (X(62.0), Y(54.5))):
        lz = top(x, y)
        w.rounded_box(f"lamp_frame{x:.0f}", (x, y, lz - 0.3), (4.4, 5.2, 1.6), m["grey3"], bevel=0.5)
        w.rounded_box(f"lamp{x:.0f}", (x, y, lz + 0.4), (2.8, 3.6, 1.0), m["lamp"], bevel=0.45)
    sz = top(0.0, Y(61.0))
    w.tube("stalk", [(0.0, Y(56.0), hz + 3.0), (0.0, Y(61.0), sz + 1.6), (0.0, Y(67.0), top(0.0, Y(67.0)) + 1.2)], 2.3,
           m["grey7"], 14)
    for yy in (Y(59.5), Y(63.0)):
        w.lathe_axis(f"stalk_ring{yy:.0f}", [(-0.4, 2.3), (-0.2, 2.8), (0.2, 2.8), (0.4, 2.3)], m["grey3"],
                     (0.0, yy, top(0.0, yy) + 1.5), (0, 1, -0.1), 14)
    # The eye in its ring, its lids drawn half over it.
    ex, ey = 0.0, Y(74.0)
    ez = top(ex, ey) + 1.8
    w.hoop("eye_ring", (ex, ey, ez - 1.0), [(5.2, -1.6), (8.4, -1.2), (8.8, 0.4), (7.6, 1.6), (5.6, 1.4), (4.8, 0.4)],
           m["grey5"], 40)
    w.hoop("eye_ring_hi", (ex, ey, ez + 0.6), [(7.4, -0.3), (8.0, -0.2), (7.9, 0.25), (7.3, 0.2)], m["grey9"], 40)
    w.sphere("socket", (ex, ey, ez - 1.0), (5.6, 5.6, 1.6), m["black"], 24, 8)
    w.sphere("eye", (ex, ey, ez - 0.4), (4.2, 4.2, 2.6), m["eye"], 24, 12)
    w.sphere("eye_core", (ex - 0.8, ey + 0.8, ez + 1.9), (1.5, 1.5, 0.6), m["eye_core"], 12, 6)
    for s in (-1, 1):
        lid = w.sphere(f"lid{s}", (ex, ey + s * 1.6, ez + 0.1), (4.9, 3.6, 2.6), m["grey7"], 24, 10)
        sh.cut_planes([lid], [((ex, ey + s * 1.4, 0), (0, -s, 0))])
    # The green lamps on the lobes.
    for x in (X(33.5), X(63.5)):
        lz = top(x, Y(87.5))
        w.rounded_box(f"lobe_lamp_frame{x:.0f}", (x, Y(87.5), lz - 0.3), (4.4, 8.6, 1.6), m["grey3"], bevel=0.5)
        w.rounded_box(f"lobe_lamp{x:.0f}", (x, Y(87.5), lz + 0.4), (2.8, 7.0, 1.0), m["lamp"], bevel=0.45)


PIECES = [(153, 0, 0), (155, 1, 0), (157, 2, 0), (159, 3, 0),
          (191, 0, 1), (193, 1, 1), (195, 2, 1), (197, 3, 1),
          (229, 0, 2), (241, 1, 2), (243, 2, 2), (235, 3, 2),
          (267, 0, 3), (269, 1, 3), (271, 2, 3)]


def shell_piece(i, j):
    shell_whole()
    w.bake()
    x0 = -48 + 24 * i if j < 3 else -36 + 24 * i
    y1 = 56 - 28 * j
    w.piece(w.meshes(), x0, x0 + 24, y1 - 28, y1)


for sprite, i, j in PIECES:
    model(f"green_shell_{sprite}", [(J, sprite, True)])(lambda i=i, j=j: shell_piece(i, j))


w.run()
