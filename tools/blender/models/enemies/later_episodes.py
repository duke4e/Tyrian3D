"""The most frequent enemies of episodes 2-5 (each appears more than 100 times), facing the way their
sprites do (models.cfg: yaw=0). Flames, lava and the parts of large structures stay volumetric.

(crystal_blue, crystal_small, eye_ring, fan, orb_red, orb_eyes, sphere_nozzle, lava_ball, donut,
disc_spokes, panel_gems, panel_pills, ring_machine, bolt, arrow_purple, blob_red, ship_blue, cone_ship and
claw_ship are built by polish_<name>.py, blob_big and drops by polish_blobs.py, block_x and
block_chevron by polish_blocks.py.)
"""
import os
import sys


sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
import tyrkit as k  # noqa: E402
import silhouette as s  # noqa: E402


def rows(text):
    return [line for line in text.strip("\n").split("\n")]


def export(name):
    here = os.path.dirname(os.path.abspath(__file__))
    k.export(os.path.join(here, "..", "..", "..", "..", "assets", "models", "enemies", name + ".glb"))


def silhouette_ship(name, art, body_index, wing_index, max_radius=2.6, thickness=1.4):
    k.reset()
    body = k.material(name + "_body", palette=body_index, metallic=0.45, roughness=0.35)
    wings = k.material(name + "_wings", palette=wing_index, metallic=0.4, roughness=0.4)
    r = rows(art)
    s.plate("wings", r, -thickness / 2, thickness / 2, wings, bevel=0.35)
    s.fuselage("fuselage", r, body, max_radius=max_radius)
    export(name)


def drill():
    k.reset()
    grey = k.material("drill_grey", palette=6, metallic=0.65, roughness=0.3)
    dark = k.material("drill_dark", palette=3, metallic=0.5, roughness=0.5)
    # Wide at the top (row 0), a point at the bottom (row 27).
    body = k.lathe("drill", [(-13.5, 0.2), (-10.0, 2.0), (-4.0, 4.5), (3.0, 7.0), (10.0, 9.0), (13.5, 9.6)], grey,
                   segments=24, axis_z=8.0, squash=0.85)
    k.smooth(body, 50)
    for i, y in enumerate((-8.0, -2.0, 4.0, 10.0)):
        r = 2.0 + (y + 13.5) / 27 * 7.6
        k.smooth(k.lathe(f"thread{i}", [(y - 0.7, r + 0.1), (y, r + 0.7), (y + 0.7, r + 0.1)], dark, segments=24,
                         axis_z=8.0, squash=0.85), 60)
    export("drill")


BOMBER = """
.######o#########o#o####
.####ooo#########ooo####
..###o.o#########o.o###.
...##o.o#########o.o##..
....oo.o#########o.oo...
.......o#########o......
.......o#oo###oo#o......
.......o#oo###oo#o......
.......o#########o......
.......o#oo###oo#o......
.......o#oo###oo#o......
.......o#########o......
........##o#ooo##.......
........##o#ooo##.......
........###ooo###.......
........#########.......
.........#######........
.........#######........
.........#######........
..........#####.........
..........#####.........
...........###..........
...........###..........
............#...........
........................
........................
........................
........................
"""

def ships():
    # (ship_blue, cone_ship and claw_ship: polish_<name>.py)
    silhouette_ship("bomber", BOMBER, 7, 5, max_radius=4.2, thickness=1.8)


drill()
ships()
