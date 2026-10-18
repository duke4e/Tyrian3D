"""Batch F of the second wave, continued (wave2_f.py has the rest), facing the way the sprites do
(models.cfg: yaw=0). Larger objects the game draws from several sprites are built whole and cut
into the sprites' pieces, which are drawn at their own origins (models.cfg: origin) so they meet:

- arch_left, arch_right (sheet 2 49, 2 51): episode 1's purple and grey arch, two curved arms over a
  small hub with two red thrusters hanging from it. (2 49 had a flat plate model, arch_ship.)
- grabber_left, grabber_right (sheet 2 123, 2 125): the grey grabber of TYRIAN and FLEET with a
  glowing blue bar down its neck and two hooked legs, standing on the ground.
- drillrig_head, drillrig_bit (sheet V 1, V 39): the drilling machine of GRYPHON, MISTAKES and
  STATION: a blue armoured head and the spiral drill below it. (V 39 had a stand-alone drill.)
- asteroid_tl, asteroid_tr, asteroid_bl, asteroid_br (sheet D 7, 9, 45, 47): the big lumpy asteroid
  of the asteroid levels, lying on the ground.
- pod_dome (sheet C 163): the ground relative of DELI's flying pod machine (pod_turret, C 191, is built by
  polish_pod_turret.py): a blue double dome, the two pods and the grey
  gun pointing down the screen with blue lights at its muzzle.

usage: blender -b --factory-startup -P wave2_f_more.py -- [--only name,name] [--preview <prefix>]
       [--check <directory of the extracted sheets>] [--stats 1] [--whole <prefix>]
--whole renders the whole objects (<prefix><object>_top.png, _3q.png).
"""
import math
import os
import sys

import bpy
from mathutils import Matrix, Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave2_f_kit as w  # noqa: E402
from wave2_f_kit import k, sh, model, pal  # noqa: E402


def X(col, ox=24):
    """A pixel column's centre in a combined object's coordinates."""
    return col + 0.5 - ox


def Y(row, oy=14):
    return oy - (row + 0.5)


# --- The arch (sheet 2 49 and 51) ---------------------------------------------------------------
# a grey, p purple plates, t the thrusters' rods and brace, r the red thrusters.

ARCH = w.art("""
............#####a###......######a##............
..........##aaaaappppp....#pppppaaaa##..........
........##aaagaaappppp#..#pppppppaaaaaa##.......
......##aaaaaaaaappapp#..#ppppppppaaaaaaa##.....
.....#aaaaaaa######p#####a##p####a#a#aaaaa#.....
.....#aaaaaa#aaaaa###aa##aa###aaaaa##aaaaa#.....
.....#aaaaaaagaaaa#aaaaaaaaaa#aaaaaaa##aa##.....
.....#aaaaaaagaaaa###aaaaaa###aaaaaaaaa####.....
.....#aaaaaaaaa####.#tt#ttt#.####aaaaaaaa##.....
...##aaaaaaaaa#.....#tt##tt#.....aaaaaaaaaa##...
..#appppppaaa#......#t####t#......#aaapppppa#...
..#pppppppaa#.......#t#..#t#.......#aappppppp#..
..#pppppppa#......###tt###t###......#appppppp#..
..#pppppaa#.......#tttt##tttt#.......#ppppppp#..
..#pppppaa........##t#t##t#t##........#appppp#..
..#ppppaaa........#tttt##tttt#........#appppa#..
..#pppaaaa........#t#tt##tt#t#........#aaappp#..
..#ppaaaa#........###t####t###........#aaaapa#..
..#aaaapa#.........#rr#..#rr#.........#ppaaaa#..
..#aaappa#.........#rr#..#rr#.........#ppaaaa#..
..#aapppa#.........#rr#..#rr#.........#pppaaa#..
..#appppa#.........#rr#..arr#..........#pppaa#..
..#appa#...........#rr#..#rr#...........#ppaa#..
..#ppp#............#r#....#r#............#paa#..
..#pp#.............##......##.............#aa#..
..#a#......................................#a#..
..##........................................##..
................................................
""")


# The purple plates (pixel edges, column and row): on the top band near the middle, and two on each
# arm's lower part, split by a grey stripe.
ARCH_PLATES = [
    [(17.2, 1.2), (21.8, 1.2), (21.8, 3.8), (17.2, 3.8)],
    [(3.3, 10.3), (9.8, 10.3), (9.8, 12.8), (8.0, 13.6), (5.2, 17.8), (3.3, 17.8)],
    [(7.0, 18.2), (7.9, 18.2), (7.9, 21.8), (5.6, 24.2), (4.2, 24.8), (3.3, 24.8), (3.3, 23.0), (4.0, 21.0)],
    [(27.2, 1.2), (32.8, 1.2), (32.8, 3.8), (27.2, 3.8)],
    [(38.2, 10.3), (44.7, 10.3), (44.7, 17.8), (42.8, 17.8), (40.0, 13.6), (38.2, 12.8)],
    [(39.1, 18.2), (40.0, 18.2), (41.6, 20.4), (42.8, 22.0), (42.8, 23.8), (42.0, 23.8), (39.1, 20.6)],
]


def arch_whole():
    """The whole arch, centred on the line between its two sprites (art column 24)."""
    hull = pal("arch2_hull", 6, metallic=0.6, roughness=0.32)
    light = pal("arch2_light", 9, metallic=0.6, roughness=0.28)
    plate = pal("arch2_plate", 90, metallic=0.4, roughness=0.3)
    dark = pal("arch2_dark", 3, metallic=0.5, roughness=0.45)
    red = pal("arch2_red", 117, roughness=0.25, glow=1.6, emission=(255, 50, 20))
    hot = pal("arch2_hot", 120, roughness=0.2, glow=3.0, emission=(255, 150, 60))
    origin = (24, 14)
    arms = w.relabel(ARCH, [("#tr", ".", 18, 29, 8, 26)])
    polys = sh.outlines(arms, "#apg", origin, smooth=2, epsilon=0.5, min_area=2.0)

    def shape(x, y, z):
        # The arms are highest along their middles; a seam where the top band meets the arms.
        return z - 0.5 * math.exp(-((y - Y(4.2)) / 0.4) ** 2) * (abs(x) > 4.5)
    body = sh.inflate("arms", polys, hull, sh.pillow_profile(3.0, 0.9, crown=0.4), bottom=0.0, spacing=0.65,
                      z_fn=shape)
    k.smooth(body, 50)
    top = lambda x, y: sh.surface_z(body, x, y, 3.0)
    # The purple plates, a little proud of the arms.
    for i, outline in enumerate(ARCH_PLATES):
        poly = [(c - origin[0], origin[1] - r) for c, r in outline]
        pl = sh.inflate(f"plate{i}", [poly], plate, sh.pillow_profile(0.7, 0.5), bottom=0.0, base=0.0, spacing=0.55)
        for v in pl.data.vertices:
            v.co.z += top(v.co.x, v.co.y) - 0.12
        k.smooth(pl, 45)
    # Ribs across the arms where the sprite has bright lines.
    for side in (-1, 1):
        w.tube(f"rib{side}", w.catmull([(side * 13.5, Y(5.5), 3.6), (side * 11.0, Y(7.5), 3.7),
                                        (side * 10.5, Y(9.5), 3.6)], 0.6), 0.4, light, 8)
    # The hub under the middle of the top band, the two rods, the brace between them, the thrusters.
    w.rounded_box("hub", (0.0, Y(5.5), 2.4), (11.0, 4.6, 3.6), hull, bevel=0.8)
    for side in (-1, 1):
        x = side * 2.5
        w.lathe_axis(f"rod{side}", [(0.0, 1.0), (10.5, 1.0)], light, (x, Y(7.0), 2.2), (0, -1, 0), 12,
                     squash=0.9)
        w.lathe_axis(f"collar{side}", [(0.0, 1.2), (0.2, 1.5), (1.4, 1.5), (1.6, 1.2)], dark, (x, Y(16.2), 2.2),
                     (0, -1, 0), 14)
        w.lathe_axis(f"thruster{side}", [(-0.01, 0.01), (0.0, 1.15), (4.5, 1.15), (5.4, 0.8), (5.7, 0.01)], red,
                     (x, Y(17.8), 2.2), (0, -1, 0), 16)
        w.sphere(f"thruster_hot{side}", (x, Y(22.6), 2.2), (0.6, 0.6, 0.6), hot, 10, 6)
    w.rounded_box("brace", (0.0, Y(14.5), 2.4), (11.6, 5.0, 2.2), hull, bevel=0.7)
    for side in (-1, 1):
        w.rounded_box(f"brace_light{side}", (side * 2.0, Y(14.2), 3.5), (1.0, 3.4, 0.6), light, bevel=0.25)
    w.rounded_box("brace_slot", (0.0, Y(14.5), 3.45), (1.4, 3.8, 0.5), dark, bevel=0.2)


@model("arch_left", "enemy_2", 49)
def arch_left():
    arch_whole()
    w.bake()
    w.piece(w.meshes(), -24, 0, -14, 14)


@model("arch_right", "enemy_2", 51)
def arch_right():
    arch_whole()
    w.bake()
    w.piece(w.meshes(), 0, 24, -14, 14)


# --- The grabber (sheet 2 123 and 125) ----------------------------------------------------------
# a grey, j glowing blue, d blue trim, g dark blue trim, i teal trim.

GRABBER = w.art("""
...................########.....................
..................#aajjjjaa#....................
..................#aajjjjaa#....................
..................#aajjjjaa#....................
..................#aajjjjaa#....................
.................#aaaaaaaaa##...................
................#aaaajjjj#aaa#..................
..............#######jjjd#######................
..............#######jjjd#######................
..............#aaaaa#jjjd#aaaaa#................
............###aaaaa#jjjd#aajaa###..............
............#iiijjia#jjjd#aajiiid#..............
............#d#aaaaa#jjjd#aaaaa#d#..............
............#d#aaaa##djdd##aaaa#g#..............
............#d#aaa##aadd#a##gaa#g#..............
............#d#aai#aa#aaa###iaa#d#..............
............#d#aai#aaa#a##a#iaa#g#..............
............###aai#aaa#a#aa#iaa###..............
..............#aai##aa#aaa##iaa#................
............###aai#.#a#aa#.#iaa##g#.............
............daaaai#..####..#iaaaai#.............
............daaaai#........#iaaaai#.............
............ddaaai#........#iaaadd#.............
............ddaaai#........#iagddg#.............
............#ddddd#........#ddddg#..............
............#gdddd#........#ddddg#..............
.............#gggg#........#gggg#...............
..............#####........#####................
""")


def grabber_whole():
    """The grabber, standing on the ground: a grey neck with a blue light, shoulders over a dark
    joint, two legs with blue and teal trims ending in hooked blue claws, and a glowing blue bar
    down the middle between them."""
    hull = pal("grab_hull", 6, metallic=0.6, roughness=0.32)
    light = pal("grab_light", 8, metallic=0.6, roughness=0.28)
    dark = pal("grab_dark", 2, metallic=0.5, roughness=0.5)
    blue = pal("grab_blue", 58, metallic=0.4, roughness=0.25)
    deep = pal("grab_deep", 101, metallic=0.4, roughness=0.3)
    teal = pal("grab_teal", 132, metallic=0.35, roughness=0.25)
    glow = pal("grab_glow", 155, roughness=0.15, glow=1.6, emission=(70, 130, 255))
    hot = pal("grab_glow_hot", 159, roughness=0.15, glow=2.4, emission=(150, 210, 255))
    origin = (24, 14)
    # The legs and shoulders: everything but the neck and the middle.
    legs = w.relabel(GRABBER, [("#aidgj", ".", 19, 26, 0, 27), ("#aj", ".", 16, 29, 0, 6)])
    leg_polys = sh.outlines(legs, "#aidgj", origin, smooth=2, epsilon=0.5, min_area=2.0)

    def leg_top(x, y, z):
        # Lower towards the claws.
        return z * (0.75 + 0.25 * sh.smoothstep(Y(26), Y(12), y))
    body = sh.inflate("legs", leg_polys, hull, sh.pillow_profile(3.8, 0.9, crown=0.3), bottom=0.0, spacing=0.65,
                      z_fn=leg_top)
    k.smooth(body, 50)
    # The neck and the dark joint under it.
    neck = [(X(18) - 0.3, Y(0) + 0.3), (X(27) + 0.3, Y(0) + 0.3), (X(27) + 0.4, Y(5)), (X(29) + 0.3, Y(6.5)),
            (X(29) + 0.3, Y(9)), (X(16) - 0.3, Y(9)), (X(16) - 0.3, Y(6.5)), (X(18) - 0.3, Y(5))]
    k.smooth(sh.inflate("neck", [neck], light, sh.pillow_profile(5.4, 1.2, crown=0.4), bottom=0.0, spacing=0.65),
             50)
    joint = [(X(14) - 0.2, Y(7) + 0.4), (X(31) + 0.2, Y(7) + 0.4), (X(31) + 0.2, Y(9) - 0.4),
             (X(14) - 0.2, Y(9) - 0.4)]
    k.smooth(sh.inflate("joint", [joint], dark, sh.pillow_profile(3.4, 0.6), bottom=0.0, spacing=0.6), 45)
    # The dark middle between the legs, low.
    middle = [(X(19) - 0.3, Y(9)), (X(26) + 0.3, Y(9)), (X(26) + 0.2, Y(18)), (X(24), Y(20.6)), (X(21), Y(20.6)),
              (X(19) - 0.2, Y(18))]
    k.smooth(sh.inflate("middle", [middle], dark, sh.round_profile(0.6, max_height=2.6), bottom=0.0, spacing=0.6),
             50)
    # The glowing blue: the light on the neck and the bar down the middle, set in grey rims.
    w.rounded_box("neck_light", (X(22.5), Y(2.5), 5.6), (4.2, 4.2, 1.4), glow, bevel=0.5)
    w.sphere("neck_light_hot", (X(22.0), Y(1.8), 6.15), (0.7, 0.7, 0.35), hot, 12, 6)
    bar = [(X(22), Y(6), 5.0), (X(22), Y(9), 4.8), (X(22), Y(12.5), 3.8), (X(22.3), Y(14.5), 2.6)]
    w.tube("bar", w.catmull(bar, 0.6), 1.25, glow, 12)
    w.tube("bar_rim", w.catmull([(X(23.8), Y(6.5), 4.4), (X(23.8), Y(12.6), 3.4)], 0.6), 0.45, blue, 8)
    # The trims along the legs: blue outside, teal inside, the claws' tips dark blue.
    top = lambda x, y: sh.surface_z(body, x, y, 2.0)
    lines = [  # (pixel path (column, row), radius, material)
        ([(13.0, 10.8), (13.0, 19.0), (12.8, 22.0), (13.6, 24.8), (15.6, 26.0), (17.2, 25.6)], 0.6, blue),
        ([(17.5, 12.0), (17.5, 18.5), (17.4, 23.2)], 0.45, teal),
        ([(13.0, 10.9), (16.8, 10.9)], 0.45, teal),
        ([(32.6, 10.8), (32.6, 19.5), (33.0, 22.6), (32.0, 25.2), (30.0, 26.0), (28.4, 25.4)], 0.6, deep),
        ([(28.3, 12.0), (28.3, 18.5), (28.3, 23.2)], 0.45, teal),
        ([(28.6, 10.9), (32.4, 10.9)], 0.45, teal),
    ]
    for i, (path, radius, mat) in enumerate(lines):
        pts = [(X(c), Y(r), 0.0) for c, r in path]
        pts = [(x, y, top(x, y) + 0.1) for x, y, _ in w.catmull(pts, 0.6)]
        w.tube(f"trim{i}", pts, radius, mat, 8)
    # The claws' blue tips, hooking inwards.
    for side, (c, r) in ((-1, (14.5, 24.5)), (1, (31.0, 24.5))):
        base = Vector((X(c), Y(r), 1.6))
        w.blade(f"claw{side}", base, base + Vector((-side * 3.2, -2.0, -0.3)),
                [(0.0, 1.4, 1.2, 0.9), (0.6, 0.8, 0.7, 0.5)], blue if side < 0 else deep, sides=8)
    # Knuckles where the legs leave the shoulders.
    for x in (X(17.0), X(29.0)):
        w.sphere(f"knuckle{x}", (x, Y(10.5), 4.6), (1.5, 1.3, 0.9), light, 14, 8)


@model("grabber_left", "enemy_2", 123)
def grabber_left():
    grabber_whole()
    w.bake()
    w.piece(w.meshes(), -24, 0, -14, 14)


@model("grabber_right", "enemy_2", 125)
def grabber_right():
    grabber_whole()
    w.bake()
    w.piece(w.meshes(), 0, 24, -14, 14)


# --- The drilling machine (sheet V 1 and 39) ----------------------------------------------------
# One object 24 x 56 pixels: the head is the upper sprite (V 1), the drill the lower (V 39).

DRILL_PROFILE = [(17, 7.6), (19, 8.2), (21, 9.3), (23, 10.0), (26, 10.1), (28, 9.4), (31, 8.3), (35, 7.1), (39, 6.1),
                 (43, 5.0), (47, 3.3), (51, 2.0), (54, 0.9)]


def drillrig_whole():
    """The drilling machine lying on the ground, its drill pointing down the screen: a blue armoured
    head (a tall block in the middle, a sloping plate on the left, a grey hatch open at the front, a
    grey piston on the right) on the drill's wide shoulder; the drill a cone with two spiral threads."""
    Xd = lambda c: c + 0.5 - 12
    Yd = lambda r: 28 - (r + 0.5)
    armour = pal("drill_armour", 56, metallic=0.45, roughness=0.28)
    plate = pal("drill_plate", 59, metallic=0.45, roughness=0.25)
    edge = pal("drill_edge", 53, metallic=0.4, roughness=0.35)
    steel = pal("drill_steel", 11, metallic=0.6, roughness=0.25)
    grey = pal("drill_grey", 7, metallic=0.7, roughness=0.3)
    thread = pal("drill_thread", 9, metallic=0.65, roughness=0.3)
    dark = pal("drill_dark", 3, metallic=0.5, roughness=0.5)
    ax, az, squash = 0.5, 6.4, 0.66
    # The drill: turned along -Y, its threads two helices just proud of it.
    prof = [(Yd(55) - 0.1, 0.05)] + [(Yd(r), rad) for r, rad in reversed(DRILL_PROFILE)]
    bit = k.lathe("drill", k.profile(prof, 1.0), steel, segments=28, axis_x=ax, axis_z=az, squash=squash)
    k.smooth(bit, 60)
    radius = lambda y: next((r for yy, r in reversed(k.profile(prof, 0.3)) if yy <= y), 0.05)
    for start in (0.0, math.pi):
        pts = []
        y = Yd(22)
        while y > Yd(52):
            t = start + (Yd(22) - y) * 2 * math.pi / 9.0
            r = radius(y) + 0.2
            pts.append((ax + r * math.cos(t), y, az + squash * r * math.sin(t)))
            y -= 0.6
        w.tube(f"thread{start:.0f}", pts, 0.7, thread, 7)
    # The head's body: a rounded hull over the drill's shoulder, flat underneath.
    body = [(Xd(1) - 0.2, Yd(4)), (Xd(4), Yd(1) + 0.3), (Xd(17) + 0.3, Yd(1) + 0.3), (Xd(18) + 0.4, Yd(4)),
            (Xd(21) + 0.3, Yd(10)), (Xd(22) + 0.3, Yd(13)), (Xd(22) + 0.3, Yd(15.5)), (Xd(20), Yd(17.5)),
            (Xd(3), Yd(17.5)), (Xd(2) - 0.3, Yd(15)), (Xd(1) - 0.3, Yd(9))]
    k.smooth(sh.inflate("head", [body], armour, sh.pillow_profile(9.0, 3.0, crown=0.8), bottom=0.0, spacing=0.8),
             50)
    # The tall block at the top middle with its lighter face, and the sloping plate on the left.
    w.rounded_box("tower", (Xd(12.8), Yd(4.9), 11.2), (9.4, 9.6, 7.0), plate, bevel=1.8)
    w.rounded_box("tower_face", (Xd(12.8), Yd(4.6), 14.6), (6.4, 6.6, 0.6), armour, bevel=0.3)
    pad = w.rounded_box("pauldron", (0, 0, 0), (7.6, 8.8, 4.0), plate, bevel=1.4)
    pad.data.transform(Matrix.Translation((Xd(4.8), Yd(5.2), 10.4)) @ Matrix.Rotation(math.radians(-16), 4, "Y"))
    w.rounded_box("pauldron_rim", (Xd(4.6), Yd(9.6), 10.0), (7.0, 1.0, 1.6), edge, bevel=0.4)
    # The column down the front middle and the plates on the right.
    w.rounded_box("column", (Xd(13), Yd(13.2), 10.0), (3.0, 8.2, 3.0), plate, bevel=0.9)
    for i, (c, r, sx, sy, z) in enumerate(((17.2, 11.6, 4.2, 3.8, 10.2), (19.6, 14.8, 4.4, 4.0, 9.4))):
        w.rounded_box(f"side_plate{i}", (Xd(c), Yd(r), z), (sx, sy, 2.4), plate, bevel=0.8)
    # The open hatch at the front left: grey machinery in a dark frame.
    w.rounded_box("hatch", (Xd(8.6), Yd(13.2), 8.9), (6.2, 6.4, 0.8), dark, bevel=0.3)
    w.lathe_axis("hatch_drum", [(0.0, 0.01), (0.05, 1.7), (5.0, 1.7), (5.05, 0.01)], grey,
                 (Xd(6.2), Yd(12.4), 9.6), (1, 0, 0), 16)
    w.lathe_axis("hatch_drum2", [(0.0, 0.01), (0.05, 1.2), (4.0, 1.2), (4.05, 0.01)], steel,
                 (Xd(6.7), Yd(15.3), 9.2), (1, 0, 0), 14)
    # The grey piston on the right.
    w.lathe_axis("piston", [(0.0, 0.01), (0.05, 1.6), (4.0, 1.6), (4.3, 1.2), (6.6, 1.2), (6.8, 0.01)], grey,
                 (Xd(19.6), Yd(4.6), 9.6), (0, -1, 0), 16)
    w.rounded_box("piston_mount", (Xd(18.8), Yd(8.2), 9.6), (3.0, 3.0, 2.6), steel, bevel=0.6)
    sh.flat_bottom(w.meshes())


@model("drillrig_head", "enemy_V", 1)
def drillrig_head():
    drillrig_whole()
    w.bake()
    w.piece(w.meshes(), -12, 12, 0, 28)


@model("drillrig_bit", "enemy_V", 39)
def drillrig_bit():
    drillrig_whole()
    w.bake()
    w.piece(w.meshes(), -12, 12, -28, 0)


# --- The big asteroid (sheet D 7, 9, 45, 47) -----------------------------------------------------
# The sprites' shades (0-f, the grey ramp) from row 3 of the 48 x 56 object (its outline).

ASTEROID_TOP_ROW = 3
ASTEROID = w.art("""
................................................
................................000.............
...............................013100...........
..............................014543100.........
.............................0146a7543100.......
............................01469b996543100.....
...........................014679b8997444310....
..........................014679aaba95764430....
.................0011100.014579aa898569864410...
................014444311134589987558bb987530...
...............014787654444466677578cb88885410..
...............0368aa99666544556799bb986677530..
..............0147aaa9997875456899bb98a867a7410.
.............01479aab9998885558999b9868677b7530.
............01479aaaba99998655899ac877777797431.
...........01468aaaabb99999874799bc879a87787430.
...........03689aaaaabb999986558a9b879987685410.
..........01489aaaaabacb9999767757987898678531..
..........03699aaaaababcb9997788866877757a7431..
..........14799aaaaababbc9988889a8688466797431..
..........14699aaaaabbabcb97899999747568787430..
..........03589aaaababbcbb87acdc99954648776410..
..........01469aaaabbbbbbaa8bcfdba99744588541...
...........0347aaaaabbbbba97bceaaaa9964477431...
...........01468aabbcbbbba89bcdb99ca984456431...
............0356aabbbbb98768acc9b99aa9544541....
............0145778898987758acc88b8aa9464431....
.............034465875667748acb8999a965784410...
.............014459cb98766489ba9aa99778974430...
.............0147acbaa9967688a9c99957899865410..
............0146acba9aaa88579baaa976a999976430..
...........01468cb999b9aaa856899767ca9a8987431..
...........03689dbaaaa99aaa7668968cc9999a88431..
...........1479adcba9aaba99a64656cd88887889431..
...........1489adca9ab999aa998659ca88788976430..
..........01699bcbaa9aaaa99999747bb87898774310..
.........014799acbba99ab999988875688888775410...
........0146999acdccbbaa98777887746787876530....
.......0146899999cbdcba987766778864556565410....
.......0368999999998889a8767787777844444410.....
.......146999999998888a9776677767765444410......
.......1347888898888899854455667877444430.......
.......03446777777788975aa877778766446310.......
.......013444678887777858765666666544410........
........0013444665555556666686665544430.........
..........00134444555445666666554444310.........
............00134444444554566544333100..........
..............0013444445544444311100............
................0013444443331100................
..................00133311100...................
....................0011........................
""")


# The boulders the asteroid is made of (the lobes the sprites draw): centre (column, row), radii in
# pixels, height, shade (palette index), turn (degrees).
BOULDERS = [
    ((35.0, 10.0), (6.6, 5.6), 8.5, 9, 20), ((39.4, 19.5), (5.0, 7.0), 8.0, 8, -10),
    ((19.5, 21.0), (8.8, 9.2), 11.0, 10, 15), ((32.0, 29.8), (5.6, 6.6), 10.0, 10, -20),
    ((41.0, 33.0), (4.4, 6.6), 7.0, 8, 0), ((19.0, 39.6), (8.8, 7.6), 10.0, 9, -10),
    ((27.6, 46.6), (8.6, 5.6), 8.0, 8, 5), ((35.4, 40.4), (5.6, 5.6), 8.5, 9, 30),
    ((12.6, 43.0), (4.6, 5.6), 6.5, 8, 0), ((25.0, 30.5), (4.4, 4.0), 8.0, 9, 0),
]


def asteroid_whole():
    """The big asteroid on the ground: a cluster of lumpy grey boulders where the sprites draw their
    lobes, packed on a low dark base that fills the cracks between them."""
    base = pal("asteroid_base", 6, metallic=0.05, roughness=0.8)
    oy = 28 - ASTEROID_TOP_ROW
    polys = sh.outlines(ASTEROID, "0123456789abcdef", (24, oy), smooth=2, epsilon=0.6, min_area=4.0)
    k.smooth(sh.inflate("base", [sh.inset(p, 0.8) for p in polys], base, sh.round_profile(0.5, max_height=2.6),
                        bottom=0.0, spacing=0.9, sigma=2.0), 60)
    for i, ((c, r), (rx, ry), h, shade, turn) in enumerate(BOULDERS):
        mat = pal(f"asteroid_rock{shade}", shade, metallic=0.05, roughness=0.75)
        rock = w.lumpy(f"boulder{i}", (0, 0, 0), (rx * 1.08, ry * 1.08, h * 0.85), mat, seed=11 + i, amount=0.2,
                       segments=14, rings=9)
        rock.data.transform(Matrix.Translation((c + 0.5 - 24, 28 - (r + 0.5), -0.1 * h)) @
                            Matrix.Rotation(math.radians(turn), 4, "Z"))
        k.smooth(rock, 32)
    sh.flat_bottom(w.meshes())


def asteroid_piece(x0, x1, y0, y1):
    asteroid_whole()
    w.bake()
    w.piece(w.meshes(), x0, x1, y0, y1)


@model("asteroid_tl", "enemy_D", 7)
def asteroid_tl():
    asteroid_piece(-24, 0, 0, 28)


@model("asteroid_tr", "enemy_D", 9)
def asteroid_tr():
    asteroid_piece(0, 24, 0, 28)


@model("asteroid_bl", "enemy_D", 45)
def asteroid_bl():
    asteroid_piece(-24, 0, -28, 0)


@model("asteroid_br", "enemy_D", 47)
def asteroid_br():
    asteroid_piece(0, 24, -28, 0)


# --- The pod machines (sheet C 191 and C 163) -----------------------------------------------------

def pod_parts(prefix, flip, mats):
    """What the two machines share: two blue-grey pods either side with dark bores, and the grey gun
    housing along the middle with two dark slots, pointing up the screen (flip 1) or down (-1)."""
    px, py = w.px, w.py
    pod, rim, grey, light, dark = mats
    # The pods: short cylinders standing up out of the hull, leaning outwards and towards the gun's end.
    for side in (-1, 1):
        base = Vector((side * 7.0, 0.0, 1.0))
        axis = Vector((side * 0.35, flip * 0.45, 1.0)).normalized()
        w.lathe_axis(f"{prefix}pod{side}", [(0.0, 3.6), (4.2, 3.6), (4.5, 3.3), (4.6, 0.01)], pod, base, axis, 24)
        w.lathe_axis(f"{prefix}pod_rim{side}", [(0.0, 3.3), (0.3, 3.95), (0.9, 3.95), (1.2, 3.4)], rim,
                     base + axis * 3.6, axis, 24)
        w.lathe_axis(f"{prefix}pod_bore{side}", [(0.0, 0.01), (0.05, 2.1), (0.6, 2.1), (0.65, 0.01)], dark,
                     base + axis * 4.3, axis, 16)
        w.lathe_axis(f"{prefix}pod_band{side}", [(0.0, 3.55), (0.2, 3.85), (0.8, 3.85), (1.0, 3.55)], rim,
                     base + axis * 1.2, axis, 24)
    # The gun housing: a grey cylinder along the middle with a rounded end and slots on top.
    end = py(3) if flip > 0 else py(24.6)
    start = py(12.5) if flip > 0 else py(13.5)
    length = abs(end - start)
    w.lathe_axis(f"{prefix}gun", [(0.0, 3.8), (length - 2.6, 4.1), (length - 1.2, 3.6), (length - 0.3, 2.4),
                                  (length, 0.01)], grey, (0.0, start, 4.4), (0, flip, 0), 24, squash=0.95)
    for i, x in enumerate((-1.7, 1.7)):
        y = (start + end) / 2 - flip * 0.8
        w.rounded_box(f"{prefix}slot{i}", (x, y, 8.15), (1.9, length * 0.6, 1.0), dark, bevel=0.35)
    w.lathe_axis(f"{prefix}gun_collar", [(0.0, 4.1), (0.3, 4.5), (1.4, 4.5), (1.7, 4.1)], light,
                 (0.0, start + flip * 0.4, 4.4), (0, flip, 0), 24, squash=0.95)


def pod_materials(prefix):
    return (pal(prefix + "_pod", 106, metallic=0.55, roughness=0.3), pal(prefix + "_podrim", 108, metallic=0.55,
                                                                        roughness=0.25),
            pal(prefix + "_grey", 8, metallic=0.65, roughness=0.3), pal(prefix + "_greylight", 9, metallic=0.65,
                                                                       roughness=0.25),
            pal(prefix + "_dark", 1, metallic=0.4, roughness=0.6))


@model("pod_dome", "enemy_C", 163)
def pod_dome():
    """The pod machine on the ground: a blue double dome at the top, a blue-grey band across the
    middle carrying the two pods, and the grey gun pointing down the screen, two blue lights at its
    muzzle."""
    px, py = w.px, w.py
    mats = pod_materials("podd")
    blue = pal("podd_blue", 56, metallic=0.4, roughness=0.28)
    band = mats[1]
    light = pal("podd_light", 59, roughness=0.2, glow=1.5, emission=(80, 160, 255))
    for side in (-1, 1):
        k.smooth(k.ellipsoid(f"dome{side}", (side * 5.8, py(5.8), 0.0), (6.3, 4.9, 6.4), blue, 32, 14), 60)
    w.rounded_box("band", (0.0, py(11.8), 2.8), (23.4, 4.2, 5.4), band, bevel=1.4)
    pod_parts("", -1, mats)
    for x in (-1.5, 1.5):
        w.sphere(f"muzzle_light{x}", (x, py(25.6), 4.0), (0.8, 0.9, 0.8), light, 12, 6)
    sh.flat_bottom(w.meshes())


# --- Main ----------------------------------------------------------------------------------------

WHOLE = {"arch": (arch_whole, (48, 28)), "grabber": (grabber_whole, (48, 28)), "drillrig": (drillrig_whole, (24, 56)),
         "asteroid": (asteroid_whole, (48, 56))}


def whole(prefix, only=None):
    for name, (build, size) in WHOLE.items():
        if only and name not in only:
            continue
        k.reset()
        build()
        w.bake()
        bpy.context.scene.view_settings.view_transform = "Standard"
        k.preview(prefix + name, size, scale=10)
        scene = bpy.context.scene
        cam = bpy.data.objects["3q"]
        cam.location = Vector((38, -48, 42)) * (max(size) / 40)
        scene.render.resolution_x, scene.render.resolution_y = 768, 768
        scene.render.filepath = prefix + name + "_3q.png"
        bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    options = k.args()
    if "whole" in options:
        whole(options["whole"], set(options["only"].split(",")) if "only" in options else None)
    else:
        w.main()
