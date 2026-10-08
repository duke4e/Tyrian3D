"""The most frequent enemies of episodes 2-5 (each appears more than 100 times), facing the way their
sprites do (models.cfg: yaw=0). Flames, lava and the parts of large structures stay volumetric.
"""
import math
import os
import sys

import bpy
from mathutils import Vector

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


def cone(name, base, tip, radius, mat, vertices=12):
    base, tip = Vector(base), Vector(tip)
    axis = tip - base
    bpy.ops.mesh.primitive_cone_add(vertices=vertices, radius1=radius, radius2=0.0, depth=axis.length,
                                    location=(base + tip) / 2)
    obj = bpy.context.active_object
    obj.name = name
    obj.rotation_euler = axis.to_track_quat("Z", "Y").to_euler()
    obj.data.materials.append(mat)
    return obj


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


def gem(name, centre, half_w, half_d, height, mat, sides=8, table=0.55):
    """A faceted gem lying on the ground: a table on top, the girdle, the pavilion to a point below."""
    cx, cy, cz = centre
    verts = [(cx, cy, cz + height)]
    for i in range(sides):
        a = 2 * math.pi * (i + 0.5) / sides
        verts.append((cx + half_w * table * math.cos(a), cy + half_d * table * math.sin(a), cz + height))
    for i in range(sides):
        a = 2 * math.pi * i / sides
        verts.append((cx + half_w * math.cos(a), cy + half_d * math.sin(a), cz + height * 0.45))
    verts.append((cx, cy, cz - height * 0.3))
    faces = []
    n = sides
    for i in range(n):
        j = (i + 1) % n
        faces.append((0, 1 + i, 1 + j))
        faces.append((1 + i, 1 + n + i, 1 + n + j))
        faces.append((1 + i, 1 + n + j, 1 + j))
        faces.append((1 + n + i, 1 + 2 * n, 1 + n + j))
    obj = k.mesh_object(name, verts, faces, mat)
    k.recalc_normals(obj)
    return obj


def silhouette_ship(name, art, body_index, wing_index, max_radius=2.6, thickness=1.4):
    k.reset()
    body = k.material(name + "_body", palette=body_index, metallic=0.45, roughness=0.35)
    wings = k.material(name + "_wings", palette=wing_index, metallic=0.4, roughness=0.4)
    r = rows(art)
    s.plate("wings", r, -thickness / 2, thickness / 2, wings, bevel=0.35)
    s.fuselage("fuselage", r, body, max_radius=max_radius)
    export(name)


# --- Gems, blocks and plates ---------------------------------------------------------------------

def crystals():
    k.reset()
    blue = k.material("crystal_blue", palette=156, metallic=0.3, roughness=0.1, emission=(40, 100, 255),
                      emission_strength=0.35)
    gem("crystal", pos(11.5, 13.5), 9.6, 11.6, 7.0, blue)
    export("crystal_blue")
    k.reset()
    blue = k.material("crystal_blue", palette=156, metallic=0.3, roughness=0.1, emission=(40, 100, 255),
                      emission_strength=0.35)
    gem("crystal", pos(5.5, 6.5, small=True), 4.8, 5.6, 4.0, blue)
    export("crystal_small")


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
    """A grey plate with three red capsules standing in it (sheet S 153 and 191)."""
    k.reset()
    plate = k.material("pills_plate", palette=6, metallic=0.5, roughness=0.45)
    red = k.material("pills_red", palette=116, metallic=0.2, roughness=0.2, emission=(200, 20, 0),
                     emission_strength=0.25)
    k.pillow("plate", 11.6, 13.6, 3.0, plate, rounding=1.4, dome=0.3)
    for x in (-6.5, 0.0, 6.5):
        k.smooth(k.lathe(f"pill{x}", [(-9.0, 0.3), (-8.0, 2.0), (-6.5, 2.6), (6.5, 2.6), (8.0, 2.0), (9.0, 0.3)], red,
                         segments=16, axis_x=x, axis_z=3.4, squash=0.8), 60)
    export("panel_pills")


def panel_gems():
    """A grey plate with a cross of grooves and two red gems (sheet D 127)."""
    k.reset()
    plate = k.material("gems_plate", palette=6, metallic=0.5, roughness=0.45)
    dark = k.material("gems_dark", palette=3, metallic=0.4, roughness=0.6)
    red = k.material("gems_red", palette=118, metallic=0.3, roughness=0.15, emission=(220, 30, 0),
                     emission_strength=0.4)
    k.pillow("plate", 11.6, 13.6, 3.5, plate, rounding=1.6, dome=0.4)
    k.box("groove_x", (0, 0, 3.6), (20.0, 1.6, 0.6), dark)
    k.box("groove_y", (0, 0, 3.6), (1.6, 24.0, 0.6), dark)
    for y in (4.0, -4.0):
        gem(f"gem{y}", (0.0, y, 3.4), 2.6, 3.0, 2.2, red, sides=6)
    export("panel_gems")


def disc_spokes():
    k.reset()
    brown = k.material("disc_brown", palette=19, metallic=0.5, roughness=0.45)
    light = k.material("disc_light", palette=22, metallic=0.55, roughness=0.35)
    red = k.material("disc_red", palette=117, roughness=0.25, emission=(255, 40, 0), emission_strength=0.8)
    c = pos(11.5, 13.5)
    k.smooth(k.ellipsoid("disc", (c[0], c[1], 1.5), (11.4, 11.4, 3.0), brown, 40, 10), 50)
    for i in range(8):
        a = math.radians(22.5 + 45 * i)
        dx, dy = math.cos(a), math.sin(a)
        stroke(f"spoke{i}", [(c[0] + dx * 3.5, c[1] + dy * 3.5), (c[0] + dx * 9.8, c[1] + dy * 9.8)], 1.0, 2.6, 4.0,
               light)
    k.smooth(k.ellipsoid("eye", (c[0], c[1], 3.8), (3.0, 3.0, 1.6), red, 16, 8), 60)
    export("disc_spokes")


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
    orb("orb_red", 11.5, 14, 7.6, 114, lights=((-2.5, 2.0), (2.5, 2.0)))
    export("orb_red")
    orb("orb_eyes", 12, 14, 10.0, 113, lights=((-3.2, 2.5), (3.2, 2.5)))
    export("orb_eyes")
    c = orb("sphere_nozzle", 12.5, 12, 8.2, 108)
    steel = k.material("nozzle_steel", palette=106, metallic=0.6, roughness=0.3)
    fire = k.material("nozzle_fire", palette=121, roughness=0.3, emission=(255, 110, 20), emission_strength=1.6)
    base, tip = Vector((c[0] + 5.5, c[1] - 5.5, c[2])), Vector((c[0] + 10.5, c[1] - 9.0, c[2]))
    cone("nozzle", tip, base, 3.2, steel)
    k.smooth(k.ellipsoid("flame", tuple(tip + (tip - base).normalized() * 0.6), (1.8, 1.8, 1.8), fire, 12, 6), 60)
    export("sphere_nozzle")
    k.reset()
    lava = k.material("lava_ball", palette=121, roughness=0.5, emission=(255, 90, 10), emission_strength=1.2)
    k.smooth(k.ellipsoid("ball", pos(11.5, 13, 9.0), (10.8, 10.8, 9.2), lava, 32, 16), 70)
    export("lava_ball")
    k.reset()
    blue = k.material("donut_blue", palette=55, metallic=0.4, roughness=0.25)
    torus("donut", pos(11.5, 12, 3.6), 7.4, 3.8, blue)
    export("donut")


def blobs():
    k.reset()
    red = k.material("blob_red", palette=115, metallic=0.15, roughness=0.2)
    for i, (col, row, r) in enumerate([(10.5, 11.5, 8.4), (6, 9, 4.8), (14, 8, 4.6), (12, 16, 4.6)]):
        k.smooth(k.ellipsoid(f"blob{i}", pos(col, row, r * 0.7), (r, r, r * 0.8), red, 24, 12), 70)
    export("blob_red")
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


def fan():
    k.reset()
    grey = k.material("fan_blades", palette=9, metallic=0.6, roughness=0.3)
    red = k.material("fan_hub", palette=118, roughness=0.3, emission=(255, 40, 0), emission_strength=0.8)
    c = pos(11.5, 12.5, 3.0)
    for i in range(4):
        a = math.radians(45 + 90 * i)
        blade = k.ellipsoid(f"blade{i}", (c[0] + math.cos(a) * 6.8, c[1] + math.sin(a) * 6.8, c[2]),
                            (6.2, 3.6, 1.2), grey, 20, 8)
        blade.data.transform(__import__("mathutils").Matrix.Translation(-Vector((c[0] + math.cos(a) * 6.8,
                                                                                    c[1] + math.sin(a) * 6.8, c[2]))))
        blade.rotation_euler = (0, math.radians(12), a)
        blade.location = (c[0] + math.cos(a) * 6.8, c[1] + math.sin(a) * 6.8, c[2])
        k.smooth(blade, 60)
    k.smooth(k.ellipsoid("hub", c, (2.8, 2.8, 2.2), red, 16, 8), 60)
    export("fan")


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


def eye_ring():
    k.reset()
    red = k.material("eyering_red", palette=119, roughness=0.3, emission=(255, 60, 0), emission_strength=0.9)
    eye = k.material("eyering_eye", palette=58, metallic=0.3, roughness=0.15)
    pupil = k.material("eyering_pupil", palette=114, roughness=0.3, emission=(200, 20, 0), emission_strength=0.6)
    c = pos(11.5, 13.5, 2.5)
    torus("ring", c, 9.6, 1.8, red)
    k.smooth(k.ellipsoid("eye", (c[0], c[1], c[2] + 0.5), (5.8, 4.2, 3.0), eye, 24, 12), 60)
    k.smooth(k.ellipsoid("pupil", (c[0], c[1], c[2] + 2.8), (1.0, 3.2, 0.9), pupil, 12, 8), 60)
    export("eye_ring")


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


SHIP_BLUE = """
........................
........................
..........oooooo........
.........o######o.......
........o########o......
........o##ooo###o......
........ooo####ooo......
........o#o####o#o......
........ooo####ooo......
.......o##o####o##o.....
.....ooo#oo####oooooo...
.....o##############o...
.....o##############o...
.....o##############o...
......o############o....
.......ooo######ooo.....
.........o######o.......
.......ooo######ooo.....
.......o##########o.....
.......o##########o.....
........o########o......
........o########o......
.........o######o.......
.........o######o.......
..........o####o........
...........oooo.........
........................
........................
"""

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

CONE_SHIP = """
........................
........................
........................
........................
........................
............#...........
...........###..........
.........######o........
.........#######........
.......o########oo......
......o###########o.....
.....o#####o#o#####o....
....o###############o...
....o######o#o######o...
....o###############o...
.....oo####o#o####oo....
......o####ooo####o.....
......o####o.o####o.....
......o####o.o####o.....
.......o###o.o###o......
.......o###o.o###o......
.......o###o.o###o......
........o##o.o##o.......
........o##o.o##o.......
.........o#o.o#o........
.........o#o.o#o........
..........oo.oo.........
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

CLAW_SHIP = """
.........oooo...........
.......o#####oo.........
......o########o........
.....o##########o.......
.....o##########o.......
.....o##########o.......
.....ooo######ooo.......
.......o######o.........
.....ooo######ooo.......
.....o###o##o###o.......
.....o###oooo###o.......
...ooo###o..o###ooo.....
...o#####o..o#####o.....
...o#####o..o#####o.....
...o#####o..o#####o.....
...o#####o..o#####o.....
...o###ooo..ooo###o.....
...o###o......o###o.....
...o###o......o###o.....
...o###o......o###o.....
...o###o......o###o.....
....o##o......o##o......
....o##o......o##o......
.....o#o......o#o.......
.....o#o......o#o.......
......oo......oo........
........................
........................
"""


def ships():
    silhouette_ship("ship_blue", SHIP_BLUE, 56, 53, max_radius=3.2, thickness=2.0)
    silhouette_ship("bomber", BOMBER, 7, 5, max_radius=4.2, thickness=1.8)
    silhouette_ship("cone_ship", CONE_SHIP, 10, 7, max_radius=2.6, thickness=2.2)
    silhouette_ship("claw_ship", CLAW_SHIP, 9, 6, max_radius=4.0, thickness=2.4)
    # The purple arrowhead: a thick plate with a ridge along it.
    k.reset()
    purple = k.material("arrow_purple", palette=89, metallic=0.35, roughness=0.3)
    dark = k.material("arrow_dark", palette=83, metallic=0.4, roughness=0.4)
    plate = s.plate("plate", rows(ARROW), 0.0, 2.6, purple, bevel=1.0)
    k.smooth(plate, 35)
    s.fuselage("ridge", rows(ARROW), dark, max_radius=2.4)
    export("arrow_purple")


crystals()
block_x()
block_chevron()
panel_pills()
panel_gems()
disc_spokes()
orbs()
blobs()
fan()
ring_machine()
eye_ring()
drill()
bolt()
ships()
