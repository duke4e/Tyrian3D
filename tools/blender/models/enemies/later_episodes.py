"""The most frequent enemies of episodes 2-5 (each appears more than 100 times), facing the way their
sprites do (models.cfg: yaw=0). Flames, lava and the parts of large structures stay volumetric.

(crystal_blue, crystal_small, eye_ring, fan, orb_red, sphere_nozzle, lava_ball, disc_spokes, panel_gems,
blob_red, ship_blue, cone_ship and claw_ship are built by polish_<name>.py.)
"""
import math
import os
import sys

import bpy

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
import tyrkit as k  # noqa: E402
import silhouette as s  # noqa: E402


def pos(col, row, z=0.0, small=False):
    """A sprite pixel's centre as model coordinates (2x2 sprite 24 x 28, 1x1 12 x 14)."""
    w, h = (12, 14) if small else (24, 28)
    return (col + 0.5 - w / 2, h / 2 - (row + 0.5), z)


def rows(text):
    return [line for line in text.strip("\n").split("\n")]


def export(name):
    here = os.path.dirname(os.path.abspath(__file__))
    k.export(os.path.join(here, "..", "..", "..", "..", "assets", "models", "enemies", name + ".glb"))


def torus(name, centre, major, minor, mat, rotation=(0, 0, 0)):
    bpy.ops.mesh.primitive_torus_add(major_radius=major, minor_radius=minor, major_segments=40, minor_segments=12,
                                     location=centre, rotation=rotation)
    obj = bpy.context.active_object
    obj.name = name
    obj.data.materials.append(mat)
    return k.smooth(obj, 60)


def ccw(outline):
    area = sum(outline[i][0] * outline[(i + 1) % len(outline)][1] - outline[(i + 1) % len(outline)][0] * outline[i][1]
               for i in range(len(outline)))
    return outline if area > 0 else outline[::-1]


def stroke(name, path, half_width, z0, z1, mat):
    """A raised line along a path (an emblem on a top)."""
    left, right = [], []
    for i, (x, y) in enumerate(path):
        ax, ay = path[max(i - 1, 0)]
        bx, by = path[min(i + 1, len(path) - 1)]
        dx, dy = bx - ax, by - ay
        length = math.hypot(dx, dy) or 1.0
        nx, ny = -dy / length * half_width, dx / length * half_width
        left.append((x + nx, y + ny))
        right.append((x - nx, y - ny))
    return k.slab(name, ccw(left + right[::-1]), z0, z1, mat)


def silhouette_ship(name, art, body_index, wing_index, max_radius=2.6, thickness=1.4):
    k.reset()
    body = k.material(name + "_body", palette=body_index, metallic=0.45, roughness=0.35)
    wings = k.material(name + "_wings", palette=wing_index, metallic=0.4, roughness=0.4)
    r = rows(art)
    s.plate("wings", r, -thickness / 2, thickness / 2, wings, bevel=0.35)
    s.fuselage("fuselage", r, body, max_radius=max_radius)
    export(name)


# --- Gems, blocks and plates ---------------------------------------------------------------------

def block_x():
    k.reset()
    k.pillow("block", 11.0, 12.6, 9.0, k.material("blockx_shell", palette=87, metallic=0.05, roughness=0.3),
             dome=1.2)
    red = k.material("blockx_red", palette=119, metallic=0.2, roughness=0.3)
    top = 10.2
    stroke("x1", [(-5.0, 5.5), (5.0, -5.5)], 1.2, top - 0.5, top + 0.6, red)
    stroke("x2", [(-5.0, -5.5), (5.0, 5.5)], 1.2, top - 0.5, top + 0.6, red)
    export("block_x")


def block_chevron():
    k.reset()
    k.pillow("block", 11.0, 12.6, 9.0, k.material("chevron_shell", palette=71, metallic=0.05, roughness=0.3),
             dome=1.2)
    dark = k.material("chevron_dark", palette=68, metallic=0.1, roughness=0.4)
    top = 10.2
    for dy in (3.5, -1.5):
        stroke(f"chevron{dy}", [(-5.5, dy - 3.0), (0.0, dy + 1.5), (5.5, dy - 3.0)], 0.9, top - 0.5, top + 0.4, dark)
    export("block_chevron")


def panel_pills():
    """Three red capsules, each lying in its own grey cradle on the ground (sheet S 191 draws them up the
    screen, 153 across it). The grey round them in the sprites is the map's floor: no plate under them."""
    k.reset()
    grey = k.material("pills_plate", palette=8, metallic=0.5, roughness=0.4)
    red = k.material("pills_red", palette=116, metallic=0.2, roughness=0.2, emission=(200, 20, 0),
                     emission_strength=0.25)
    for x in (-8.0, 0.0, 8.0):  # S 191's columns 1-6, 9-14, 17-22
        k.pillow(f"cradle{x}", 3.7, 9.9, 1.8, grey, rounding=0.8, dome=0.1).location = (x, 0.0, 0.0)
        k.smooth(k.lathe(f"pill{x}", [(-9.0, 0.4), (-8.6, 1.5), (-8.0, 2.2), (-7.2, 2.65), (-6.2, 2.8),
                                            (6.2, 2.8), (7.2, 2.65), (8.0, 2.2), (8.6, 1.5), (9.0, 0.4)], red,
                         segments=16, axis_x=x, axis_z=2.3, squash=0.85), 60)
    export("panel_pills")


# --- Round ones ----------------------------------------------------------------------------------

def orb(name, col, row, radius, index, lights=(), light_color=(255, 120, 20), z=None):
    k.reset()
    shell = k.material(name + "_shell", palette=index, metallic=0.25, roughness=0.25)
    glow = k.material(name + "_light", palette=121, roughness=0.3, emission=light_color, emission_strength=1.5)
    c = pos(col, row, radius * 0.8 if z is None else z)
    k.smooth(k.ellipsoid("orb", c, (radius, radius, radius * 0.85), shell, 32, 16), 70)
    for i, (dx, dy) in enumerate(lights):
        k.smooth(k.ellipsoid(f"light{i}", (c[0] + dx, c[1] + dy, c[2] + radius * 0.6), (1.4, 1.4, 1.0), glow, 12, 6), 60)
    return c


def orbs():
    # (orb_red: polish_orb_red.py)
    orb("orb_eyes", 12, 14, 10.0, 113, lights=((-3.2, 2.5), (3.2, 2.5)))
    export("orb_eyes")
    # (sphere_nozzle, lava_ball: polish_sphere_nozzle.py, polish_lava_ball.py)
    k.reset()
    blue = k.material("donut_blue", palette=55, metallic=0.4, roughness=0.25)
    torus("donut", pos(11.5, 12, 3.6), 7.4, 3.8, blue)
    export("donut")


def blobs():
    # (blob_red: polish_blob_red.py)
    k.reset()
    red = k.material("blob_red", palette=115, metallic=0.15, roughness=0.2)
    for i, (col, row, r) in enumerate([(11, 12, 10.2), (6, 8, 5.0), (15, 18, 5.0)]):
        k.smooth(k.ellipsoid(f"blob{i}", pos(col, row, r * 0.7), (r, r, r * 0.8), red, 24, 12), 70)
    export("blob_big")
    k.reset()
    red = k.material("drops_red", palette=117, metallic=0.15, roughness=0.15, emission=(200, 30, 0),
                     emission_strength=0.3)
    for i, (col, row, rx, ry) in enumerate([(6, 9, 4.6, 5.2), (18, 9, 4.6, 5.2), (12, 19, 4.6, 6.2)]):
        k.smooth(k.ellipsoid(f"drop{i}", pos(col, row, 3.4), (rx, ry, 3.6), red, 24, 12), 70)
    export("drops")


def ring_machine():
    k.reset()
    grey = k.material("ringm_grey", palette=7, metallic=0.6, roughness=0.35)
    red = k.material("ringm_red", palette=116, roughness=0.3, emission=(220, 30, 0), emission_strength=0.5)
    c = pos(12, 13, 3.0)
    torus("ring", c, 8.0, 2.8, grey)
    for i, a in enumerate((90, 210, 330)):
        r = math.radians(a)
        k.smooth(k.ellipsoid(f"pod{i}", (c[0] + math.cos(r) * 8.6, c[1] + math.sin(r) * 9.4, c[2] + 1.2),
                             (2.8, 2.8, 2.4), red, 16, 8), 60)
    export("ring_machine")


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


def bolt():
    k.reset()
    grey = k.material("bolt_grey", palette=5, metallic=0.65, roughness=0.3)
    red = k.material("bolt_red", palette=117, roughness=0.3, emission=(220, 30, 0), emission_strength=0.6)
    # The silhouette's half widths from the bottom (row 26) to the top (row 0).
    profile = [(-12.5, 0.6), (-11.5, 2.0), (-10.0, 3.5), (-8.0, 4.8), (-5.0, 5.4), (-1.5, 5.0), (0.0, 3.2),
               (3.5, 3.0), (5.5, 2.4), (7.0, 1.6), (8.0, 2.6), (10.0, 4.6), (11.5, 6.0), (13.0, 6.2), (13.6, 5.0)]
    k.smooth(k.lathe("bolt", profile, grey, segments=24, axis_z=6.0, squash=0.85), 45)
    k.smooth(k.lathe("band", [(-1.0, 4.4), (0.0, 5.6), (1.0, 4.4)], red, segments=24, axis_z=6.0, squash=0.85), 60)
    export("bolt")


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

ARROW = """
............#...........
...........###..........
..........#####.........
.........#######........
........#########.......
......#############.....
.....###############....
....#################...
....#################...
....#################...
....#################...
....#################...
.....###############....
.....###############....
.....###############....
.....###############....
.....###############....
.....###############....
......#############.....
......#############.....
.......###########......
........#########.......
.........#######........
...........###..........
........................
........................
........................
........................
"""

def ships():
    # (ship_blue, cone_ship and claw_ship: polish_<name>.py)
    silhouette_ship("bomber", BOMBER, 7, 5, max_radius=4.2, thickness=1.8)
    # The purple arrowhead: a thick plate with a ridge along it.
    k.reset()
    purple = k.material("arrow_purple", palette=89, metallic=0.35, roughness=0.3)
    dark = k.material("arrow_dark", palette=83, metallic=0.4, roughness=0.4)
    plate = s.plate("plate", rows(ARROW), 0.0, 2.6, purple, bevel=1.0)
    k.smooth(plate, 35)
    s.fuselage("ridge", rows(ARROW), dark, max_radius=2.4)
    export("arrow_purple")


block_x()
block_chevron()
panel_pills()
orbs()
blobs()
ring_machine()
drill()
bolt()
ships()
