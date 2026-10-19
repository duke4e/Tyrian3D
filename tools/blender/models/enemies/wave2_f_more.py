"""Batch F of the second wave, continued (wave2_f.py has the rest), facing the way the sprites do
(models.cfg: yaw=0). Larger objects the game draws from several sprites are built whole and cut
into the sprites' pieces, which are drawn at their own origins (models.cfg: origin) so they meet (the drilling
machine, V 1 above V 39, is built by polish_drillrig.py, the arch, 2 49 beside 2 51, by polish_arch.py, the big asteroid, D 7 9 / 45 47, by
polish_asteroids.py, the pod dome, C 163, by polish_pod_dome.py):

- grabber_left, grabber_right (sheet 2 123, 2 125): the grey grabber of TYRIAN and FLEET with a
  glowing blue bar down its neck and two hooked legs, standing on the ground.

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


# --- Main ----------------------------------------------------------------------------------------

WHOLE = {"grabber": (grabber_whole, (48, 28))}


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
