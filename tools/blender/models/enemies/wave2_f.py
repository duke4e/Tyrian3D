"""Batch F of the second wave of enemy models, facing the way their sprites do (models.cfg: yaw=0)
(spike_star, 3 246: polish_spike_star.py; 7 51 is the squid ship turned round, polish_squid_ship.py; the mug of
beer, coins 241: items/polish_beer_mug.py; the pebble, D 133: polish_pebbles.py):

- obsidian_egg (sheet M 271): MINERS' indestructible black glass egg with a smoky light inside,
  lying on the ground.
- jet_steel (sheet F 79): the blue-grey jet of SAVARA, TORM and BOTANY A, its nose down the screen.


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
