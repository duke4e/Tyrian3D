"""Wave 2, batch E of the enemy models, authored as their sprites look (models.cfg: yaw=0 unless noted):

- station_end_left / station_end_right (sheet L 24 / 34): the ends of a steel axle in STATION and TIME
  WAR, at both sides of the screen with their knobs facing each other (the axle goes on into the
  background): a knob, a tube, two flanges with red lamps and a collar with red clamps, turned round
  the axle. Mirror images.
- gem_pyramid (coins 76): the small red pyramid gem worth 50 credits (items).
- face_eye (sheet 5 270): the eyeballs of NOSE DRIP's face, authored looking up the screen so that
  yaw=aim turns them after the player (the sprite looks down the screen).
- nose_bridge (sheet 5 154): the bridge of NOSE DRIP's nose; nose_tip_left / nose_tip_right (5 191 / 193)
  are the tip below it, cut from the same nose.
- deli_capsule (sheet 9 123): UNDERDELI's lilac capsule on the ground, its light band glowing (the
  frames sweep a light over it).
- facet_orb (sheet V 153, 155, 195): TIME WAR's faceted orbs, light blue, blue and green: one model
  in the blue's shades that takes each sprite's colour (color=sprite).
- eyespy_* (sheet 9 1, 3, 5, 7, 39, 45): the two armoured halves of EYESPY's robot (a domed shoulder and
  an arm ending in a gun with a blue lens), cut into the six sprites the game puts together.
- anchor_* (sheet 9 235, 236, 254, 274 and 238, 239, 258, 276): DREAD-NOT's two anchors on the ground, a
  hooded body with a gun and four struts, which the game draws from four overlapping sprites each.

The pieces of larger objects are built whole (wave2_e_parts.py, from the pixel art in wave2_e_art.py)
and cut along the sprites' edges, so they meet again in the game (models.cfg: origin).

usage: blender -b --factory-startup -P wave2_e.py -- [--only name,name] [--preview <prefix>]
       [--check <directory of the extracted sheets>] [--assembled <prefix>]
--preview renders <prefix><name>_top.png and _3q.png for each model; --check prints each model's
silhouette overlap with its sprite; --assembled renders the whole objects (<prefix><object>_top.png).
"""
import math
import os
import sys

import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
import wave1_d_shapes as sh  # noqa: E402
import wave2_e_parts as parts  # noqa: E402

ROOT = os.path.join(HERE, "..", "..", "..", "..", "assets", "models")
MODELS = []  # (name, builder, sheet file, sprite, large, directory, yaw of the preview)


def model(name, sheet, sprite, large=True, directory="enemies", preview_yaw=0.0):
    def register(fn):
        MODELS.append((name, fn, sheet, sprite, large, directory, preview_yaw))
        return fn
    return register


def lathe_x(name, profile, mat, segments=32, y=0.0, z=0.0, squash=1.0):
    """A round part along X: profile is (x, radius) pairs in increasing x."""
    obj = k.lathe(name, profile, mat, segments=segments, squash=squash)
    # Built along Y: turn so that +Y becomes +X, then place.
    obj.data.transform(Matrix.Rotation(math.radians(-90), 4, "Z"))
    obj.data.transform(Matrix.Translation((0.0, y, z)))
    return obj


def mirror_all(objects):
    for obj in objects:
        obj.data.transform(Matrix.Scale(-1, 4, (1, 0, 0)))
        obj.data.flip_normals()
        k.recalc_normals(obj)


# --- The ends of the station's axle (sheet L 24 and its mirror image 34) ----------------------------

def station_end(mirror):
    """The end of the steel axle whose knob points left (sprite 24; 34 is its mirror image), along X: a rounded
    knob, a tube, two flanges with a groove between them and small red lamps on the first one's rim,
    and a collar with red clamps at its sides, cut where the axle goes on into the background. The
    axle's centre is at y = 0.5 (rows 3-23); squashed in height."""
    steel = k.material("axle_steel", palette=9, metallic=0.5, roughness=0.3)
    bright = k.material("axle_bright", palette=11, metallic=0.5, roughness=0.25)
    dark = k.material("axle_dark", palette=4, metallic=0.6, roughness=0.45)
    red = k.material("axle_red", palette=116, metallic=0.3, roughness=0.3, emission=(220, 30, 0),
                     emission_strength=0.6)
    y0, squash = 0.5, 0.62
    objs = []
    # The knob and the tube.
    objs.append(lathe_x("knob", [(-8.0, 0.01), (-7.95, 1.6), (-7.75, 2.6), (-7.35, 3.25), (-6.8, 3.5), (-5.6, 3.5),
                                 (-5.3, 3.2), (-5.0, 3.2)], bright, y=y0, squash=squash))
    objs.append(lathe_x("tube", [(-5.3, 4.6), (-5.1, 5.3), (-4.8, 5.5), (-0.4, 5.5), (-0.1, 5.0), (0.3, 5.0)],
                        steel, y=y0, squash=squash))
    objs.append(lathe_x("tube_ring", [(-3.2, 5.3), (-3.05, 5.75), (-2.25, 5.75), (-2.1, 5.3)], dark, y=y0,
                        squash=squash))
    # The flanges, each with a chamfered rim, and the hub between them.
    for i, (a, b) in enumerate(((0.05, 3.7), (4.45, 7.95))):
        objs.append(lathe_x(f"flange{i}", [(a, 6.0), (a + 0.05, 9.6), (a + 0.45, 10.45), (b - 0.45, 10.45),
                                           (b - 0.05, 9.6), (b, 6.0)], steel, y=y0, squash=squash))
        objs.append(lathe_x(f"flange_face{i}", [(a - 0.02, 3.0), (a - 0.01, 8.6), (b + 0.01, 8.6), (b + 0.02, 3.0)],
                            dark, y=y0, squash=squash))
    objs.append(lathe_x("flange_band", [(1.6, 10.2), (1.75, 10.6), (2.25, 10.6), (2.4, 10.2)], bright, y=y0,
                        squash=squash))
    objs.append(lathe_x("hub", [(3.5, 8.3), (3.7, 8.6), (4.7, 8.6), (4.9, 8.3)], dark, y=y0, squash=squash))
    # The collar, cut at the sprite's edge.
    objs.append(lathe_x("collar", [(7.8, 6.6), (8.1, 7.2), (8.4, 7.45), (12.0, 7.45), (12.0, 0.01)], steel, y=y0,
                        squash=squash))
    objs.append(lathe_x("collar_ring", [(10.3, 7.3), (10.45, 7.75), (11.15, 7.75), (11.3, 7.3)], dark, y=y0,
                        squash=squash))
    # Red lamps on the first flange's rim, up and down the screen.
    for side in (1, -1):
        lamp = k.ellipsoid(f"lamp{side}", (3.0, y0 + side * 9.8, 0.0), (0.75, 1.3, 1.7), red, 16, 8)
        objs.append(k.smooth(lamp, 60))
    # Red clamps at the collar's sides.
    for side in (1, -1):
        clamp = k.slab(f"clamp{side}", [(8.6, -1.2), (11.9, -1.2), (11.9, 1.2), (8.6, 1.2)], -3.3, 3.3, red,
                       bevel_width=0.35)
        clamp.data.transform(Matrix.Translation((0, y0 + side * 6.1, 0)))
        objs.append(clamp)
    for obj in objs:
        if not obj.modifiers:
            k.smooth(obj, 50)
    if mirror:
        mirror_all(objs)


model("station_end_left", "L", 24)(lambda: station_end(False))
model("station_end_right", "L", 34)(lambda: station_end(True))


# --- The pyramid gem (coins 76) ---------------------------------------------------------------------

@model("gem_pyramid", "coins", 76, large=False, directory="items")
def gem_pyramid():
    """A small red gem cut as a pyramid on a square turned 45 degrees (the sprite's diamond), its
    bright apex a small table, a shallow pyramid below the girdle."""
    red = k.material("pyramid_red", palette=70, metallic=0.25, roughness=0.15, emission=(200, 50, 30),
                     emission_strength=0.12)
    light = k.material("pyramid_table", palette=74, metallic=0.2, roughness=0.1, emission=(255, 120, 90),
                       emission_strength=0.2)
    cx, cy = 0.5, -0.5
    r, t = 6.05, 1.1  # the girdle's and the table's half-diagonals
    dirs = [(1, 0), (0, 1), (-1, 0), (0, -1)]
    verts = [(cx + dx * t, cy + dy * t, 3.6) for dx, dy in dirs]             # the table
    verts += [(cx + dx * r, cy + dy * r, 0.45) for dx, dy in dirs]           # the girdle's top
    verts += [(cx + dx * r, cy + dy * r, -0.35) for dx, dy in dirs]          # the girdle's bottom
    verts.append((cx, cy, -2.9))                                             # the pavilion's point
    faces = [(0, 1, 2, 3)]
    for i in range(4):
        j = (i + 1) % 4
        faces.append((i, 4 + i, 4 + j, j))          # the crown
        faces.append((4 + i, 8 + i, 8 + j, 4 + j))  # the girdle
        faces.append((8 + i, 12, 8 + j))            # the pavilion
    obj = k.mesh_object("gem", verts, faces)
    k.recalc_normals(obj)
    obj.data.materials.append(red)
    obj.data.materials.append(light)
    obj.data.polygons[0].material_index = 1
    k.bevel(obj, 0.18, 1)


# --- NOSE DRIP's eye (sheet 5 270) ------------------------------------------------------------------

@model("face_eye", "5", 270, preview_yaw=180.0)
def face_eye():
    """A glossy eyeball, its blue iris and black pupil looking up the screen and towards the camera
    (models.cfg turns it towards the player with yaw=aim; the sprite looks down). Its centre is the
    sprite's (0.5, 1.5), radius 10.5; a little flattened."""
    white = k.material("eye_white", palette=62, metallic=0.0, roughness=0.12)
    iris = k.material("eye_iris", palette=57, metallic=0.1, roughness=0.15, emission=(40, 110, 170),
                      emission_strength=0.3)
    ring = k.material("eye_ring", palette=52, metallic=0.1, roughness=0.2)
    inner = k.material("eye_iris_inner", palette=55, metallic=0.1, roughness=0.15)
    pupil = k.material("eye_pupil", palette=48, metallic=0.2, roughness=0.06)
    cx, cy, rad, flat = -0.5, -1.5, 10.5, 0.8  # (0.5, 1.5) when turned to look down
    k.smooth(k.ellipsoid("ball", (cx, cy, 0.0), (rad, rad, rad * flat), white, 48, 24), 80)
    # The iris: a cap on the ball, turned towards (0, sin, cos) of the look's angle.
    look = math.radians(28)  # from straight up (the camera) towards +Y
    iris_angle = math.radians(35)

    def cap(name, angle, lift, mat, segments=40):
        rings = []
        steps = 8
        for i in range(1, steps + 1):
            a = angle * i / steps
            rings.append([(math.sin(a) * math.cos(2 * math.pi * s / segments),
                           math.sin(a) * math.sin(2 * math.pi * s / segments), math.cos(a)) for s in range(segments)])
        verts = [(0.0, 0.0, 1.0)]
        for rr in rings:
            verts += rr
        faces = [(0, 1 + (s + 1) % segments, 1 + s) for s in range(segments)]
        for i in range(steps - 1):
            for s in range(segments):
                a0, a1 = 1 + i * segments + s, 1 + i * segments + (s + 1) % segments
                faces.append((a0, a1, a1 + segments, a0 + segments))
        # The cap's rim tucks under the ball.
        rim = [(x * 0.97, y * 0.97, z * 0.97) for x, y, z in rings[-1]]
        base = len(verts)
        verts += rim
        last = 1 + (steps - 1) * segments
        for s in range(segments):
            faces.append((last + s, last + (s + 1) % segments, base + (s + 1) % segments, base + s))
        scaled = []
        for x, y, z in verts:
            p = Matrix.Rotation(-look, 3, "X") @ Vector((x, y, z))  # tilt towards +Y
            scaled.append((cx + p.x * (rad + lift), cy + p.y * (rad + lift), p.z * (rad + lift) * flat))
        obj = k.mesh_object(name, scaled, faces, mat)
        k.recalc_normals(obj)
        return k.smooth(obj, 80)

    # The iris in rings, dark at its rim and round the pupil, each a little proud of the last.
    cap("iris_ring", iris_angle, 0.1, ring)
    cap("iris", iris_angle * 0.88, 0.2, iris)
    cap("iris_inner", iris_angle * 0.55, 0.28, inner)
    cap("pupil", iris_angle * 0.33, 0.36, pupil)


# --- UNDERDELI's capsule (sheet 9 123) --------------------------------------------------------------

@model("deli_capsule", "9", 123)
def deli_capsule():
    """A lilac capsule standing on the ground: a rounded body (columns 3-21, rows 5-26) with raised
    rails along its sides, a glowing band across its middle (rows 13-17, where the frames sweep a
    light), a seam down its lower half and two small feet."""
    body = k.material("capsule_body", palette=87, metallic=0.35, roughness=0.35)
    rail = k.material("capsule_rail", palette=90, metallic=0.4, roughness=0.3)
    dark = k.material("capsule_dark", palette=84, metallic=0.3, roughness=0.5)
    glow = k.material("capsule_glow", palette=92, metallic=0.1, roughness=0.2, emission=(230, 190, 250),
                      emission_strength=0.45)
    rows = sh.art("""
.....###############
.....###############
...###################
...###################
...###################
...###################
...###################
...###################
...###################
...###################
...###################
....#################
....#################
....#################
....#################
....#################
....#################
....#################
....#################
....#################
.....###############
......#############
""")
    origin = (12, 14 - 5)  # the art starts at the sprite's row 5
    outline = sh.outlines(rows, "#", origin, smooth=2, epsilon=0.5)
    height = 7.0
    shell = sh.inflate("body", outline, body, sh.pillow_profile(height, 3.0, crown=1.0), bottom=0.0, spacing=0.4)
    k.smooth(shell, 45)
    cx = 0.5

    def top(x, y):
        return sh.surface_z(shell, x, y, height)

    # The glowing band across the middle (rows 14-17): a rounded light bar following the body, sunk
    # into it at its edges.
    xs = [cx - 8.3 + 16.6 * j / 40 for j in range(41)]
    ys = [-3.9 + 3.9 * i / 8 for i in range(9)]
    verts, faces = [], []
    for y in ys:
        t = (y + 3.9) / 3.9
        lift = 0.55 * math.sin(math.pi * t) - 0.15
        verts += [(x, y, top(x, y) + lift) for x in xs]
    n, m = len(xs), len(ys)
    verts += [(x, y, top(x, y) - 1.5) for y in (ys[0], ys[-1]) for x in xs]
    for i in range(m - 1):
        for j in range(n - 1):
            faces.append((i * n + j, i * n + j + 1, (i + 1) * n + j + 1, (i + 1) * n + j))
    low, high = m * n, m * n + n
    for j in range(n - 1):
        faces.append((low + j, low + j + 1, j + 1, j))                                     # the lower side
        faces.append(((m - 1) * n + j, (m - 1) * n + j + 1, high + j + 1, high + j))       # the upper side
        faces.append((low + j, high + j, high + j + 1, low + j + 1))                       # underneath
    for j in (0, n - 1):  # the ends
        faces.append(tuple([i * n + j for i in range(m)] + [high + j, low + j]))
    band = k.mesh_object("band", verts, faces, glow)
    k.recalc_normals(band)
    k.smooth(band, 50)
    # Raised rails along both sides, from the top to the bottom.
    for side in (-1, 1):
        x = cx + side * 7.3
        path = [(x, y, None) for y in [8.0 - 19.2 * j / 24 for j in range(25)]]
        sh.tube_along(f"rail{side}", path, 0.6, rail, z_of=lambda px, py: top(px, py) - 0.1)
    # The seam down the lower half and the grooves above and below the band.
    seam = [(cx, y, None) for y in [-4.6 - 6.6 * j / 12 for j in range(13)]]
    sh.tube_along("seam", seam, 0.35, dark, z_of=lambda px, py: top(px, py) - 0.2)
    for y in (0.5, -5.4):
        groove = [(cx - 6.4 + 12.8 * j / 16, y, None) for j in range(17)]
        sh.tube_along(f"groove{y}", groove, 0.3, dark, z_of=lambda px, py: top(px, py) - 0.15)
    # The feet under the bottom (row 27).
    for x in (cx - 5.0, cx + 5.0):
        foot = k.slab("foot", [(x - 0.9, -14.0), (x + 0.9, -14.0), (x + 0.9, -11.0), (x - 0.9, -11.0)], 0.0, 1.4,
                      dark, bevel_width=0.25)
        k.smooth(foot, 40)


# --- TIME WAR's faceted orbs (sheet V 153, 155, 195) -----------------------------------------------

@model("facet_orb", "V", 153)
def facet_orb():
    """A cut gem in a rounded octagon (columns 3-20, rows 5-22): a table shaped like a diamond (the
    square turned 45 degrees the sprites show), crown facets down to a dark girdle, a shallow
    pavilion. In the blue ramp's shades: models.cfg gives it each sprite's colour."""
    crown = k.material("orb_crown", palette=59, metallic=0.35, roughness=0.12, emission=(60, 110, 150),
                       emission_strength=0.1)
    table = k.material("orb_table", palette=60, metallic=0.25, roughness=0.08, emission=(150, 190, 215),
                       emission_strength=0.18)
    girdle = k.material("orb_girdle", palette=52, metallic=0.4, roughness=0.3)
    cx, cy = 0.0, 0.0
    n = 16

    def outline_r(a):
        # The sprite's outline: a circle squared off a little (radius 9).
        c, s = abs(math.cos(a)), abs(math.sin(a))
        return 9.0 / (c ** 3.0 + s ** 3.0) ** (1 / 3.0) * 0.985

    table_r, table_z = 3.7, 5.6
    star_r, star_z = 6.9, 3.0
    verts, faces, mats = [], [], []

    def add(p):
        verts.append(p)
        return len(verts) - 1

    # The table: a diamond, its corners up, left, down and right.
    table_ids = [add((cx + table_r * math.cos(math.pi / 2 * i), cy + table_r * math.sin(math.pi / 2 * i), table_z))
                 for i in range(4)]
    # Eight crown points between the table and the girdle: at the corners and between them.
    star_ids = []
    for i in range(8):
        a = math.pi / 4 * i
        r = star_r if i % 2 else star_r * 0.93
        star_ids.append(add((cx + r * math.cos(a), cy + r * math.sin(a), star_z if i % 2 else star_z + 0.4)))
    # The girdle, top and bottom.
    g_top = [add((cx + outline_r(2 * math.pi * i / n) * math.cos(2 * math.pi * i / n),
                  cy + outline_r(2 * math.pi * i / n) * math.sin(2 * math.pi * i / n), 1.1)) for i in range(n)]
    g_bot = [add((cx + outline_r(2 * math.pi * i / n) * math.cos(2 * math.pi * i / n),
                  cy + outline_r(2 * math.pi * i / n) * math.sin(2 * math.pi * i / n), -0.6)) for i in range(n)]
    bottom = add((cx, cy, -4.2))
    faces.append(tuple(table_ids)); mats.append(1)
    for i in range(4):
        c0, c1 = table_ids[i], table_ids[(i + 1) % 4]
        s_corner, s_mid, s_next = star_ids[2 * i], star_ids[2 * i + 1], star_ids[(2 * i + 2) % 8]
        faces.append((c0, s_corner, s_mid)); mats.append(0)
        faces.append((c0, s_mid, c1)); mats.append(0)
        faces.append((c1, s_mid, s_next)); mats.append(0)
    for i in range(8):
        s0, s1 = star_ids[i], star_ids[(i + 1) % 8]
        g0, g1, g2 = g_top[2 * i], g_top[2 * i + 1], g_top[(2 * i + 2) % n]
        faces.append((s0, g0, g1)); mats.append(0)
        faces.append((s0, g1, s1)); mats.append(0)
        faces.append((s1, g1, g2)); mats.append(0)
    for i in range(n):
        j = (i + 1) % n
        faces.append((g_top[i], g_bot[i], g_bot[j], g_top[j])); mats.append(2)
        faces.append((g_bot[i], bottom, g_bot[j])); mats.append(2)
    obj = k.mesh_object("orb", verts, faces)
    k.recalc_normals(obj)
    for m in (crown, table, girdle):
        obj.data.materials.append(m)
    for poly, m in zip(obj.data.polygons, mats):
        poly.material_index = m
    k.bevel(obj, 0.12, 1)


# --- The assembled objects (wave2_e_parts.py) -------------------------------------------------------

for _name, _sheet, _sprite, _builder in parts.PIECES:
    model(_name, _sheet, _sprite)(_builder)


# --- Main ----------------------------------------------------------------------------------------

def triangles(obj):
    return sum(len(poly.vertices) - 2 for poly in obj.data.polygons)


def budget(target=4800):
    """Keeps a model light: with its modifiers applied, its larger meshes (the inflated parts) are
    decimated until the whole has about `target` triangles."""
    meshes = [obj for obj in bpy.data.objects if obj.type == "MESH"]
    for obj in meshes:
        sh.apply_modifiers(obj)
    total = sum(triangles(obj) for obj in meshes)
    if total <= target:
        return total
    big = [obj for obj in meshes if triangles(obj) > 400]
    small = total - sum(triangles(obj) for obj in big)
    ratio = max(0.12, (target - small) / max(1, total - small))
    for obj in big:
        mod = obj.modifiers.new("decimate", "DECIMATE")
        mod.decimate_type = "COLLAPSE"
        mod.ratio = ratio
        mod.use_collapse_triangulate = True
        sh.apply_modifiers(obj)
    return sum(triangles(obj) for obj in meshes)


def main():
    options = k.args()
    only = set(options["only"].split(",")) if "only" in options else None
    for name, build, sheet, sprite, large, directory, preview_yaw in MODELS:
        if only and name not in only:
            continue
        k.reset()
        build()
        print(f"{name}: {budget()} triangles")
        k.export(os.path.join(ROOT, directory, name + ".glb"))
        if preview_yaw:
            for obj in bpy.data.objects:
                if obj.type == "MESH":
                    obj.data.transform(Matrix.Rotation(math.radians(preview_yaw), 4, "Z"))
        size = (24, 28) if large else (12, 14)
        if "check" in options:
            sheet_file = "coins.png" if sheet == "coins" else f"enemy_{sheet}.png"
            print(f"--- {name} (sheet {sheet} sprite {sprite})")
            k.check_silhouette(os.path.join(options["check"], sheet_file), [sprite], large)
        if "preview" in options:
            k.preview(options["preview"] + name, size)
    if "assembled" in options:
        for name, build, size in parts.ASSEMBLED:
            if only and name not in only:
                continue
            k.reset()
            build()
            k.preview(options["assembled"] + name, size, scale=8)
            # A three-quarter view from farther away, for the whole object.
            scene = bpy.context.scene
            cam = bpy.data.objects["3q"]
            cam.location = Vector((38, -48, 42)) * (max(size) / 44.0)
            scene.camera = cam
            scene.render.resolution_x, scene.render.resolution_y = 1024, 768
            scene.render.filepath = options["assembled"] + name + "_3q.png"
            bpy.ops.render.render(write_still=True)


main()
