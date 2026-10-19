"""Batch F of the second wave of enemy models, facing the way their sprites do (models.cfg: yaw=0)
(spike_star, 3 246: polish_spike_star.py; 7 51 is the squid ship turned round, polish_squid_ship.py):

- obsidian_egg (sheet M 271): MINERS' indestructible black glass egg with a smoky light inside,
  lying on the ground.
- beer_mug (coins 241): the mug of beer (the bonus item), lying with its mouth up the screen and its
  handle to the right, as the sprite draws it.
- jet_steel (sheet F 79): the blue-grey jet of SAVARA, TORM and BOTANY A, its nose down the screen.
- eye_shell (sheet G 127): the small blue shell with an eye looking out (GYGES, MISTAKES); its
  animation moves the pupil a little, the model keeps it in the middle frame's place.
- purple_shield (sheet 2 127): the purple armoured pod with blue windows (TYRIAN, HOLES).
- pebble (sheet D 133, 1x1): the small blue-grey rock of the asteroid levels.


usage: blender -b --factory-startup -P wave2_f.py -- [--only name,name] [--preview <prefix>]
       [--check <directory of the extracted sheets>] [--stats 1]
"""
import math
import os
import sys

from mathutils import Matrix, Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave2_f_kit as w  # noqa: E402
from wave2_f_kit import k, sh, model, pal, px, py  # noqa: E402


# --- The obsidian egg (sheet M 271) ------------------------------------------------------------

@model("obsidian_egg", "enemy_M", 271)
def obsidian_egg():
    """A black glass egg lying on the ground (flat underneath), a smoky light inside it along the
    streak the sprite draws from the upper left to the lower right."""
    glass = pal("egg_glass", 96, metallic=0.2, roughness=0.04, alpha=0.5)
    layers = [("smoke", 3, 0.8, (60, 64, 76), 1.0, (4.0, 8.4, 2.6)),
              ("haze", 6, 1.4, (100, 104, 118), 1.7, (3.0, 7.0, 2.1)),
              ("glow", 10, 2.4, (160, 165, 180), 2.4, (2.1, 5.6, 1.7)),
              ("core", 13, 4.0, (225, 230, 245), 3.0, (1.2, 4.0, 1.4))]
    # The sprite's outline is an ellipse 16 x 25 pixels round (0, 0.5).
    axis_z = 2.4
    k.smooth(k.ellipsoid("egg", (0.0, 0.5, axis_z), (7.75, 12.4, 6.6), glass, 48, 28), 70)
    # The smoke and its bright core, tilted along the streak (rows 9-22, leaning to the left at the top),
    # nested: each layer rises a little above the one under it, so all of them show from above.
    tilt = Matrix.Translation((0.5, -1.6, axis_z)) @ Matrix.Rotation(math.radians(-22), 4, "Z")
    for name, index, strength, colour, z, radii in layers:
        mat = pal("egg_" + name, index, roughness=0.5, glow=strength, emission=colour)
        obj = k.ellipsoid(name, (0, 0, z), radii, mat, 24, 14)
        obj.data.transform(tilt)
        k.smooth(obj, 70)
    sh.flat_bottom(w.meshes())


# --- The mug of beer (coins 241) ---------------------------------------------------------------

@model("beer_mug", "coins", 241, out=w.ITEMS)
def beer_mug():
    """A faceted glass mug lying with its mouth up the screen: amber beer in its lower part, a head
    of foam above it, a thick base and the handle on the right."""
    glass = pal("mug_glass", 10, metallic=0.4, roughness=0.03, alpha=0.24)
    rim = pal("mug_rim", 12, metallic=0.4, roughness=0.05, alpha=0.55)
    flute = pal("mug_flute", 12, metallic=0.4, roughness=0.02, alpha=0.32)
    beer = pal("mug_beer", 21, metallic=0.1, roughness=0.12, glow=0.35, emission=(170, 105, 25))
    foam = pal("mug_foam", 12, roughness=0.8)
    foam_shade = pal("mug_foam_shade", 10, roughness=0.8)
    ax, az = px(10) + 0.5, 6.6       # the mug's axis (along y) in x and height
    base_y, rim_y = py(21) + 0.3, py(5)
    r_out, r_in = 6.6, 5.7
    sides = 12                        # the facets of the glass
    # The glass: faceted outside, round inside, a thick base.
    outer = k.lathe("glass", [(base_y, r_out - 0.6), (base_y + 0.4, r_out), (rim_y - 0.3, r_out),
                              (rim_y, r_out - 0.15)], glass, segments=sides, axis_x=ax, axis_z=az)
    k.smooth(outer, 20)
    k.lathe("rim", [(rim_y - 0.9, r_out - 0.05), (rim_y - 0.8, r_out + 0.15), (rim_y - 0.05, r_out + 0.15),
                    (rim_y, r_out - 0.3), (rim_y + 0.01, 0.01)], rim, segments=sides * 2, axis_x=ax, axis_z=az)
    # The base, thick glass.
    k.lathe("base", [(base_y - 0.01, 0.01), (base_y, r_out - 0.6), (base_y + 1.6, r_out - 0.2),
                     (base_y + 1.61, 0.01)], rim, segments=sides * 2, axis_x=ax, axis_z=az)
    # The beer up to the sprite's row 12, a thin head of foam on it; the glass above is empty.
    beer_top = py(12) + 0.5
    k.smooth(k.lathe("beer", [(base_y + 1.6, 0.01), (base_y + 1.65, r_in), (beer_top, r_in), (beer_top + 0.01, 0.01)],
                     beer, segments=32, axis_x=ax, axis_z=az), 50)
    head = [(beer_top - 0.05, r_in - 0.02), (beer_top + 0.9, r_in - 0.02), (beer_top + 1.3, r_in - 0.6),
            (beer_top + 1.45, 0.01)]
    k.smooth(k.lathe("foam", head, foam, segments=32, axis_x=ax, axis_z=az), 60)
    for i, (a, s) in enumerate(((20, 0.9), (70, 0.7), (115, 1.0), (160, 0.8), (250, 0.7), (300, 0.9))):
        ang = math.radians(a)
        c = (ax + (r_in - 1.2) * math.cos(ang), beer_top + 1.0, az + (r_in - 1.2) * math.sin(ang))
        w.sphere(f"bubble{i}", c, (s, s * 0.7, s), foam if i % 2 else foam_shade, 12, 6)
    # Vertical flutes on the glass (the sprite's bright stripes).
    for i in range(sides):
        a = 2 * math.pi * (i + 0.5) / sides
        x, z = ax + (r_out - 0.05) * math.cos(a), az + (r_out - 0.05) * math.sin(a)
        w.tube(f"flute{i}", [(x, base_y + 1.0, z), (x, rim_y - 1.2, z)], 0.3, flute, 8)
    # The handle: a thick loop from the side of the mug out to the sprite's column 20.
    hx = px(20)
    path = [(ax + r_out - 0.8, py(8.5), az), (hx - 0.6, py(8.5), az), (hx + 0.3, py(9.8), az),
            (hx + 0.4, py(16.5), az), (hx - 0.4, py(18.2), az), (ax + r_out - 0.8, py(18.2), az)]
    w.tube("handle", w.catmull(path, 0.35), 1.15, rim, 16)


# --- The steel jet (sheet F 79) ----------------------------------------------------------------

@model("jet_steel", "enemy_F", 79)
def jet_steel():
    """A blue-grey jet, its nose down the screen: a long round fuselage, straight wings behind the
    middle with the cockpit between them, a tail plane and a fin at the top."""
    hull = pal("jetsteel_hull", 106, metallic=0.55, roughness=0.3)
    panel = pal("jetsteel_panel", 104, metallic=0.5, roughness=0.35)
    dark = pal("jetsteel_dark", 101, metallic=0.5, roughness=0.45)
    canopy = pal("jetsteel_canopy", 96, metallic=0.3, roughness=0.05)
    glint = pal("jetsteel_glint", 109, roughness=0.1, glow=0.4)
    nav_red = pal("jetsteel_navred", 118, roughness=0.3, glow=2.0, emission=(255, 40, 20))
    nav_green = pal("jetsteel_navgreen", 37, roughness=0.3, glow=2.0, emission=(40, 255, 60))
    exhaust = pal("jetsteel_exhaust", 120, roughness=0.3, glow=2.5, emission=(255, 140, 40))
    cx = px(12)
    # The fuselage: the sprite's middle run, nose (row 27) to tail (row 0).
    prof = [(py(27) - 0.4, 0.05), (py(26), 0.7), (py(24), 1.15), (py(22), 1.55), (py(20), 1.9), (py(18), 2.35),
            (py(16), 2.4), (py(12), 2.2), (py(9), 1.9), (py(6), 1.75), (py(4), 1.5), (py(2), 1.2), (py(0) + 0.2, 0.9),
            (py(0) + 0.45, 0.01)]
    body = k.lathe("fuselage", k.profile(prof, 0.5), hull, segments=24, axis_x=cx, axis_z=0.0, squash=0.85)
    k.smooth(body, 50)
    # The jet pipe at the tail, glowing.
    w.lathe_axis("pipe", [(0.0, 0.85), (0.3, 1.0), (0.5, 0.8)], dark, (cx, py(0) + 0.1, 0.0), (0, 1, 0), 16)
    w.sphere("flame", (cx, py(0) + 0.55, 0.0), (0.65, 0.35, 0.6), exhaust, 12, 6)
    # Main wings: rounded tips, thinner towards the tips, a little dihedral.
    wing = [(px(2) - 0.3, py(11) + 0.4), (px(22) + 0.3, py(11) + 0.4), (px(22) + 0.3, py(15) - 0.3),
            (px(20), py(16) - 0.2), (px(15), py(16) - 0.4), (px(9), py(16) - 0.4), (px(4), py(16) - 0.2),
            (px(2) - 0.3, py(15) - 0.3)]
    wing_obj = k.slab("wing", wing, -0.5, 0.35, hull, bevel_width=0.3)
    sh.apply_modifiers(wing_obj)
    for v in wing_obj.data.vertices:
        d = abs(v.co.x - cx)
        v.co.z = v.co.z * (1.0 - 0.45 * min(1.0, d / 10.5)) + 0.05 * d - 0.6
    k.smooth(wing_obj, 35)
    # Flaps along the trailing edges and the navigation lights at the tips.
    for side in (-1, 1):
        x0, x1 = (cx + side * 3.0, cx + side * 9.4)
        lo, hi = min(x0, x1), max(x0, x1)
        mid = (lo + hi) / 2
        w.rounded_box(f"flap{side}", (mid, py(15.4), -0.32 + 0.05 * abs(mid - cx)), (hi - lo, 1.5, 0.5), panel,
                      bevel=0.2)
        tip_x = cx + side * 10.6
        w.sphere(f"nav{side}", (tip_x, py(13.5), -0.1 + 0.05 * 10.6), (0.45, 0.8, 0.4),
                 nav_red if side < 0 else nav_green, 10, 6)
    # Pods under the wings near the tips (the sprite's light spots).
    for side in (-1, 1):
        x = cx + side * 8.0
        w.sphere(f"pod{side}", (x, py(12.6), -0.1 + 0.05 * 8.0), (1.1, 1.9, 0.75), panel, 16, 8)
    # The tail plane and the fin.
    tail = [(px(6) - 0.3, py(2) + 0.3), (px(18) + 0.3, py(2) + 0.3), (px(18) + 0.3, py(3) - 0.3),
            (px(16) + 0.3, py(5) - 0.2), (px(8) - 0.3, py(5) - 0.2), (px(6) - 0.3, py(3) - 0.3)]
    k.smooth(k.slab("tailplane", tail, -0.2, 0.4, hull, bevel_width=0.2), 35)
    # The fin, built in the XY plane (x: along the fuselage, y: height) and stood up on it.
    fin = k.slab("fin", [(py(5.5), 0.5), (py(0.2), 0.5), (py(0.2), 3.4), (py(1.6), 3.6)], -0.3, 0.3, hull,
                 bevel_width=0.15)
    fin.data.transform(Matrix(((0, 0, 1, cx), (1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 0, 1))))
    k.smooth(fin, 35)
    # The cockpit on the wing roots: a dark glass canopy with a glint.
    w.sphere("canopy", (cx, py(14.6), 1.25), (1.35, 2.4, 1.15), canopy, 20, 10)
    w.sphere("glint", (cx - 0.35, py(14.0), 2.2), (0.35, 0.7, 0.2), glint, 10, 6)
    # Intakes beside the cockpit.
    for side in (-1, 1):
        w.lathe_axis(f"intake{side}", [(0.0, 0.01), (0.05, 0.75), (2.6, 0.8), (3.0, 0.6)], dark,
                     (cx + side * 1.9, py(18.5), -0.1), (0, 1, 0), 12, squash=0.8)


# --- The eye in a shell (sheet G 127) ----------------------------------------------------------

@model("eye_shell", "enemy_G", 129)
def eye_shell():
    """A small blue creature: a ribbed shell arching over a big eye that looks down and to the right,
    two small hooks curling down at the shell's ends."""
    shell = pal("eyeshell_shell", 58, metallic=0.35, roughness=0.3)
    rib = pal("eyeshell_rib", 61, metallic=0.35, roughness=0.25)
    dark = pal("eyeshell_dark", 53, metallic=0.3, roughness=0.4)
    eye = pal("eyeshell_eye", 60, metallic=0.1, roughness=0.12)
    iris = pal("eyeshell_iris", 55, metallic=0.2, roughness=0.15, glow=0.4, emission=(60, 140, 200))
    pupil = pal("eyeshell_pupil", 49, metallic=0.2, roughness=0.1)
    glint = pal("eyeshell_glint", 62, roughness=0.1, glow=1.5)
    cx, cy = px(12.5), py(13.6)
    # The shell: a dome over the whole creature, two ribs arching over its top.
    dome = k.ellipsoid("dome", (cx, cy, 0.6), (6.7, 5.9, 4.4), shell, 32, 16)
    k.smooth(dome, 60)
    for i, (yc, ry) in enumerate(((cy + 0.8, 4.6), (cy + 0.2, 2.6))):
        pts = []
        for a in range(-10, 191, 10):
            t = math.radians(a)
            x, y = cx + (6.5 - 1.6 * i) * math.cos(t), yc + ry * math.sin(t)
            d = ((x - cx) / 6.7) ** 2 + ((y - cy) / 5.9) ** 2
            pts.append((x, y, 0.6 + 4.4 * math.sqrt(max(0.0, 1 - d)) + 0.1))
        w.tube(f"rib{i}", w.catmull(pts, 0.6), 0.7 - 0.1 * i, rib, 10)
    # The eye in the lower half, bulging out of the shell, turned down and to the right; its lid round it.
    ec = Vector((cx + 0.3, py(16.0), 2.6))
    w.sphere("eye", ec, (3.7, 3.2, 2.7), eye, 28, 14)
    look = Vector((0.4, -0.45, 0.8)).normalized()
    w.sphere("iris", ec + look * 2.35, (1.9, 1.8, 0.8), iris, 20, 10)
    w.sphere("pupil", ec + look * 2.75, (0.95, 1.0, 0.45), pupil, 14, 8)
    w.sphere("glint", ec + Vector((-1.2, 0.9, 2.5)), (0.55, 0.45, 0.25), glint, 10, 6)
    lid = []
    for a in range(0, 361, 20):
        t = math.radians(a)
        lid.append((ec.x + 3.9 * math.cos(t), ec.y + 3.4 * math.sin(t), ec.z + 0.6 + 0.6 * math.sin(t)))
    w.tube("lid", w.catmull(lid, 0.6), 0.45, dark, 8)
    # The hooks curling down at the shell's ends.
    for side in (-1, 1):
        x = cx + side * 6.3
        hook = [(x - side * 0.4, py(11.5), 1.8), (x + side * 0.3, py(13), 1.4), (x + side * 0.1, py(15.0), 1.0),
                (x - side * 0.6, py(15.8), 0.8)]
        w.tube(f"hook{side}", w.catmull(hook, 0.4), 0.55, dark, 8)


# --- The purple shield (sheet 2 127) -----------------------------------------------------------

SHIELD = w.art("""
........#########.......
....###ffiidddidff###...
...#fffffiidddddfffff#..
..#ffffffiiiiiiiffffff#.
.#fffffffffffffffffffff#
.#fffffffffffffffffffff#
.#fffffffffffffffffffff#
.#fffffffffffffffffffff#
.#fffffffffffffffffffff#
.#ffffffffdddddffffffff#
.#ffffffffgggggffffffff#
.#f#ffffffdddddfffff#ff#
.#f##ffffgiiiidffff##ff#
.#f##ffffffffffffff##ff#
..#fffffffffffffffffff#.
..#f##fffffffffffff#ff#.
...ff#ffffffffffff##f#..
...#fffffffffffffffff#..
....fff#ffffffff#fff#...
....#ff##ffffff##fff#...
.....#ff#fff##f#fff#....
.....#fffff##ffffff#....
......#fffffffffff#.....
......#ffiiiiiifff#.....
.......#fddddddff#......
.......#fdddgddff#......
........#ddddddf#.......
.........#######........
""")


@model("purple_shield", "enemy_2", 127)
def purple_shield():
    """A purple armoured pod shaped like a shield: a blue visor at the top, a blue window in the
    middle, a blue block at the point, a raised plate down the lower middle and dark vents round
    its lower half."""
    hull = pal("pshield_hull", 84, metallic=0.4, roughness=0.35)
    plate = pal("pshield_plate", 88, metallic=0.4, roughness=0.3)
    edge = pal("pshield_edge", 86, metallic=0.4, roughness=0.3)
    vent = pal("pshield_vent", 80, metallic=0.3, roughness=0.6)
    glass = pal("pshield_glass", 59, metallic=0.2, roughness=0.1, glow=0.5, emission=(70, 150, 200))
    teal = pal("pshield_teal", 134, metallic=0.2, roughness=0.15, glow=0.35, emission=(90, 170, 180))
    block = pal("pshield_block", 54, metallic=0.3, roughness=0.25)
    cx = px(12)
    vents = [(px(3.5), py(12.5), 0.9, 1.6, 0), (px(19.5), py(12.5), 0.9, 1.6, 0),
             (px(4.5), py(15.6), 0.9, 1.3, 30), (px(18.6), py(15.6), 0.9, 1.3, -30),
             (px(6.5), py(19.0), 1.0, 1.2, 40), (px(16.8), py(19.0), 1.0, 1.2, -40),
             (px(8.6), py(20.6), 0.9, 0.9, 0), (px(14.4), py(20.6), 0.9, 0.9, 0)]

    def carve(x, y, z):
        # A groove across the top under the visor.
        return z - 0.5 * math.exp(-((y - py(6.5)) / 0.45) ** 2) * (abs(x - cx) < 9.5)

    body = sh.outlines(SHIELD, "#fidg", (12, 14), smooth=2, epsilon=0.5)
    obj = w.inflate("hull", body, hull, sh.round_profile(0.5, max_height=5.0), bottom=0.45, sigma=1.8, z_fn=carve,
                    spacing=0.9, smooth_angle=60)
    top = lambda x, y: sh.surface_z(obj, x, y, 3.0)
    # The vents: dark ovals sunk into the hull round its lower half.
    for i, (vx, vy, rx, ry, a) in enumerate(vents):
        z = sh.surface_z(obj, vx, vy, 2.0)
        v = k.ellipsoid(f"vent{i}", (0, 0, 0), (rx, ry, 0.5), vent, 16, 8)
        v.data.transform(Matrix.Translation((vx, vy, z - 0.2)) @ Matrix.Rotation(math.radians(a), 4, "Z"))
        k.smooth(v, 60)
    # The strip from the visor down to the window (rows 3-8).
    w.rounded_box("strip", (cx, py(5.6), top(cx, py(5.6)) - 0.3), (3.6, 5.6, 1.0), plate, bevel=0.4)
    # The raised plate down the lower middle (the sprite's lighter purple, rows 13-21).
    pl = [(px(9) - 0.2, py(13) + 0.3), (px(14) + 0.2, py(13) + 0.3), (px(14) + 0.1, py(19)), (px(13), py(21.2)),
          (px(10), py(21.2)), (px(9) - 0.1, py(19))]
    plate_obj = sh.inflate("plate", [pl], plate, sh.pillow_profile(0.9, 0.6), bottom=0.0, base=0.0, spacing=0.45)
    for v in plate_obj.data.vertices:
        v.co.z += top(v.co.x, v.co.y) - 0.4
    k.smooth(plate_obj, 50)
    # The visor at the top edge, the window in the middle, the block at the point.
    w.rounded_box("visor", (cx, py(2.0), top(cx, py(2.4)) - 0.2), (6.8, 2.6, 1.6), teal, bevel=0.5)
    for i, row in enumerate((9.5, 11.5)):
        w.rounded_box(f"window{i}", (cx, py(row), top(cx, py(row)) - 0.15), (4.8, 1.3, 1.0), glass, bevel=0.35)
    w.rounded_box("window_frame", (cx, py(10.5), top(cx, py(10.5)) - 0.35), (5.6, 4.6, 0.9), edge, bevel=0.4)
    w.rounded_box("block", (cx, py(24.8), top(cx, py(24.8)) - 0.6), (7.6, 4.0, 2.0), block, bevel=0.6)
    w.rounded_box("block_lip", (cx, py(23.0), top(cx, py(23.0)) - 0.2), (7.4, 0.8, 1.1), teal, bevel=0.3)


# --- The pebble (sheet D 133, 1x1) -------------------------------------------------------------

@model("pebble", "enemy_D", 133, large=False)
def pebble():
    """A glossy blue-grey rock, rounded, a little lumpy."""
    mid = pal("pebble_mid", 103, metallic=0.45, roughness=0.22)
    w.lumpy("rock", (px(5, 6), py(6.5, 7), 0.0), (5.4, 6.0, 3.8), mid, seed=5, amount=0.2)
    w.sphere("shine", (px(4.6, 6), py(5.6, 7), 4.1), (1.0, 1.8, 0.45), pal("pebble_shine", 107, roughness=0.1), 14, 6)


# --- The twin-panel ship (sheet H 284) ---------------------------------------------------------

TWIN = w.art("""
........................
......cdfff..fffdc......
.....cfddggccggddfc.....
.....fgnnggccggnngf.....
...cc#gnngg##ggnng#cc...
.cc#a#gnnggddggnng#a#cc.
c#a#gggnnggggggnnggg#a#c
cggggggnnggddggnnggggggc
#ggggggnngg##ggnngggggg#
gggggggnnggggggnnggggggg
gggggggggggggggggggggggg
gggggggggggggggggggggggg
gggggggggggggggggggggggg
gggggggggggggggggggggggg
gggggggggggggggggggggggg
#gggga#gggggggggg#agggg#
c####f#ggggggggggcf####c
.......#ggggggggc.......
........#gggggg#........
.........#gggg#.........
..........###c..........
""")


# --- Main ----------------------------------------------------------------------------------------

if __name__ == "__main__":
    w.main()
