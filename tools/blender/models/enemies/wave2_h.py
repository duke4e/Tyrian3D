"""Enemies of wave 2, batch H, modelled as their sprites look (models.cfg: yaw=0 unless noted). (GYGES' bronze
ingot, H 93: polish_yuanbao.py.)

- desert_rock_tip (sheet 3 180): the 1x1 tip of the big tan rock of DESERTRUN and SURFACE (the rest of
  the rock is 3 162, 164, 198, 200, 202): a sloping nub cut where the rock goes on (origin).
- asteroid_turret (sheet P 13): the grey turret of ASTEROID2 with a bronze dome; its frames are eight
  headings the level picks, so the model is built pointing up the screen and aims at the player.
- fire_flap_r_top, fire_flap_r_bottom (sheet A 237, 275) and their mirror images fire_flap_l_top,
  fire_flap_l_bottom (A 7, 45): the glowing fire flaps of APPROACH, MISTAKES and SOH JIN, each two
  sprites tall, hinged on one side. Their enemies don't animate by themselves (a level event can
  make them flap): they show the first frame, the flap standing on edge, which is how they are
  modelled (origin; the whole flap is built once and cut into the two sprites' pieces).
- molten_rock (sheet L 115): a ball of lava, plates of crust between glowing cracks.
- dark_ember (sheet L 118): a dark red pod with a glowing light.
- asteroid_lumpy (sheet D 5): a grey faceted asteroid.
- twin_claw_left, twin_claw_right (sheet 3 8, 3 10): the two halves of the claw ship of SURFACE, CORE
  and ICE EXIT, back to back with a glowing core between them; each half's claws hold a flame
  (origin, mirror images).
(brain_clamp, sheet 5 166, and eyespy_eye, 5 202, are built by polish_<name>.py.)

usage: Blender -b --factory-startup -P wave2_h.py -- [--only name,name] [--preview <prefix>]
       [--check <TYR3D_EXTRACT sheets dir>] [--stats 1]
--preview renders <prefix><name>_top.png and _3q.png, --check prints each model's silhouette overlap
with its sprite, --stats the triangles per part. Helpers: wave2_h_kit.py.
"""
import math
import os
import random
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave2_h_kit as kit  # noqa: E402
from wave2_h_kit import G1, G2, k, pal, sh, smoothstep, round_edge  # noqa: E402

# --- 3 180: the tip of the big rock --------------------------------------------------------------

ROCK_TIP = G1.art("""
............
............
............
............
............
............
............
............
............
............
...........a
..........ab
..........ab
.........abb
""")


def desert_rock_tip():
    dark = pal("rock_dark", 0x12, metallic=0.0, roughness=0.8)
    mid = pal("rock_mid", 0x16, metallic=0.0, roughness=0.75)
    tan = pal("rock_tan", 0x1a, metallic=0.0, roughness=0.7)
    polys = G1.polys(ROCK_TIP, "ab", smooth=1, epsilon=0.3)
    # The right and bottom edges are the sprite's: the rock goes on there (3 162, 3 198).
    cut = (lambda a, b: (a[0] > 5.99 and b[0] > 5.99) or (a[1] < -6.99 and b[1] < -6.99))

    def top(x, y, d):
        # Rising from the outer edge into the rock, a facet a little steeper near the tip.
        return 0.3 + 1.25 * d + 0.2 * (x - 4.5)

    def mat(x, y, z, d):
        return 0 if d < 0.55 else 1 if d < 1.3 else 2

    kit.solid("tip", polys, top, 0.0, [dark, mid, tan], mat, side_mat=0, spacing=0.3, smooth_angle=35, cut=cut)


# --- L 115: the lava ball ------------------------------------------------------------------------

def molten_rock():
    """A ball of lava (11 x 13 pixels) on the ground: plates of red crust, some darker, between
    glowing cracks."""
    crust = pal("lava_crust", 0x72, metallic=0.0, roughness=0.6, glow=0.2)
    plate = pal("lava_plate", 0x75, metallic=0.0, roughness=0.45, glow=0.35)
    warm = pal("lava_warm", 0x77, metallic=0.0, roughness=0.4, glow=0.7)
    hot = pal("lava_hot", 0x7a, metallic=0.0, roughness=0.4, glow=1.3)
    white = pal("lava_white", 0x7c, metallic=0.0, roughness=0.4, glow=2.0)
    centre, radii = Vector((-0.5, -0.5, 4.4)), Vector((5.5, 6.4, 4.9))
    rng = random.Random(115)
    seeds, count = [], 46
    for i in range(count):
        zz = 1 - 2 * (i + 0.5) / count
        rr = math.sqrt(1 - zz * zz)
        a = i * math.pi * (3 - math.sqrt(5))
        v = Vector((rr * math.cos(a), rr * math.sin(a), zz)) + Vector([rng.uniform(-0.25, 0.25) for _ in range(3)])
        seeds.append(v.normalized())
    dark = [rng.random() < 0.3 for _ in seeds]
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=4, radius=1.0)
    values = []
    for v in bm.verts:
        n = v.co.normalized()
        d = sorted((n.angle(s), i) for i, s in enumerate(seeds))
        gap = d[1][0] - d[0][0]  # 0 on a crack
        heat = math.exp(-gap / 0.06)
        if dark[d[0][1]]:
            heat -= 0.35 * smoothstep(0.06, 0.2, gap)
        r = 1 - 0.06 * math.exp(-gap / 0.03) + 0.03 * smoothstep(0.04, 0.2, gap)
        v.co = centre + Vector((n.x * radii.x * r, n.y * radii.y * r, n.z * radii.z * r))
        values.append(heat)
    mesh = bpy.data.meshes.new("lava")
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new("lava", mesh)
    bpy.context.scene.collection.objects.link(obj)
    kit.band_split(obj, values, [(-9, crust), (0.0, plate), (0.18, warm), (0.4, hot), (0.78, white)],
                   smooth_angle=70)
    sh.flat_bottom([obj], 0.0)  # it lies on the ground


# --- L 118: the dark ember pod -------------------------------------------------------------------

def dark_ember():
    """A dark red pod, a rounded block lying across the sprite's diagonal, with a dome and a
    glowing light on its upper left side (the sprite's bright spot)."""
    body = pal("ember_body", 0x72, metallic=0.25, roughness=0.3)
    cap = pal("ember_cap", 0x75, metallic=0.3, roughness=0.25)
    light = pal("ember_light", 0x7b, metallic=0.0, roughness=0.2, glow=2.5, color=(255, 190, 60))
    # Built along x (the long axis), then turned 45 degrees up to the upper right.
    k.pillow("pod", 5.5, 3.95, 4.6, body, rounding=2.2, dome=1.1, power=3.0)
    # The dome with the light.
    kit.ellipsoid("dome", (0.3, 1.6, 5.0), (1.8, 1.7, 1.15), cap, 20, 10)
    kit.ellipsoid("light", (0.3, 1.75, 6.0), (0.8, 0.8, 0.5), light, 14, 7)
    kit.transform_all(Matrix.Translation((0.0, -0.5, 0)) @ Matrix.Rotation(math.radians(45), 4, "Z"))


# --- D 5: the asteroid ---------------------------------------------------------------------------

ASTEROID = G2.art("""
........................
......00000000000.......
.....0022222222100......
....0024743476322000....
....012523435632221000..
...002333477552334222000
..0022235445753355654210
..0134334755474347742420
..0244323787674457964322
..0245564469854579432332
..0244774333544774422222
..0024432244433453523220
...002322367343344432320
....02222322544244323210
....01222233433244322200
....0012224323222222210.
.....002234542222222100.
......0122543322100000..
......001232222100......
.......0011111100.......
........00000000........
""")


def _ray_polygon(poly, origin, direction):
    """The nearest distance along a ray from inside a polygon to its outline."""
    best = 1e9
    ox, oy = origin
    dx, dy = direction
    for i in range(len(poly)):
        (ax, ay), (bx, by) = poly[i], poly[(i + 1) % len(poly)]
        ex, ey = bx - ax, by - ay
        den = dx * ey - dy * ex
        if abs(den) < 1e-12:
            continue
        t = ((ax - ox) * ey - (ay - oy) * ex) / den
        u = ((ax - ox) * dy - (ay - oy) * dx) / den
        if t > 1e-6 and -1e-9 <= u <= 1 + 1e-9:
            best = min(best, t)
    return best


def asteroid_lumpy():
    """A grey asteroid over the sprite's lumpy outline: a lumpy blob through the outline, its
    surface broken into flat facets of different sizes and shades."""
    shades = [pal(f"rock_{i:x}", i, metallic=0.1, roughness=0.75)
              for i in (0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0a, 0x0b, 0x0c)]
    poly = max(G2.polys(ASTEROID, "0123456789", smooth=2, epsilon=0.3), key=len)
    cx = sum(p[0] for p in poly) / len(poly)
    cy = sum(p[1] for p in poly) / len(poly)
    height = 6.8
    centre = Vector((cx, cy, height))
    rng = random.Random(5)
    waves = [(Vector([rng.uniform(-1, 1) for _ in range(3)]).normalized() * rng.uniform(2.5, 5.5),
              rng.uniform(0, 6.3)) for _ in range(10)]

    def blob(n):
        theta = math.atan2(n.y, n.x)
        r = _ray_polygon(poly, (cx, cy), (math.cos(theta), math.sin(theta))) - 0.1
        lumps = 1 + 0.12 * sum(math.sin(w.dot(n) + phase) for w, phase in waves) / len(waves) ** 0.5
        lumps = 1 + (lumps - 1) * min(1.0, abs(n.z) * 2.0)  # the outline stays the sprite's
        return centre + Vector((n.x * r * lumps, n.y * r * lumps, n.z * height * lumps))

    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=4, radius=1.0)
    for v in bm.verts:
        n = v.co.normalized()
        jitter = 1 + rng.uniform(-0.04, 0.04) * min(1.0, abs(n.z) * 2.0)
        v.co = centre + (blob(n) - centre) * jitter
    # Faces that lie nearly in one plane become one facet.
    bmesh.ops.dissolve_limit(bm, angle_limit=math.radians(11), verts=bm.verts[:], edges=bm.edges[:])
    patches = [(Vector([rng.uniform(-1, 1) for _ in range(3)]).normalized() * rng.uniform(0.35, 0.7),
                rng.uniform(0, 6.3)) for _ in range(6)]
    for f in bm.faces:
        # Lighter and darker patches, each facet a shade or two off its patch.
        c = f.calc_center_median()
        field = sum(math.sin(w.dot(c) + phase) for w, phase in patches) / len(patches) ** 0.5
        shade = 4.2 + 2.6 * field + rng.choice((-1, 0, 0, 1))
        f.material_index = max(0, min(len(shades) - 1, int(round(shade))))
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    mesh = bpy.data.meshes.new("asteroid")
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new("asteroid", mesh)
    bpy.context.scene.collection.objects.link(obj)
    for m in shades:
        obj.data.materials.append(m)
    k.smooth(obj, 5)


# --- P 13: the turret ----------------------------------------------------------------------------

# Sprite P 15 (the turret pointing up): b the body, p the prongs either side of the barrel, d the
# dome, g the barrel, t its brass muzzle, r the red light at the back; k outline pixels.
TURRET = G2.art("""
........................
........................
..........kkk...........
..........ktk...........
..........ktk...........
..........kgk...........
........kkkgkkk.........
.......kppkgkppk........
.......kppkgkppk........
.......kppkgkppk........
.......kppkgkppk........
......kbbdddddbbk.......
.....kbbbdddddbbbk......
.....kbbbdddddbbbk......
.....kbbbdddddbbbk......
.....kbbbkkkkkbbbk......
.....kbbbbbbbbbbbk......
.....kbbbbbrrbbbbk......
......kkkkkkkkkkk.......
.......kkk...kkk........
""")


def asteroid_turret():
    """The turret pointing up the screen (sprite P 15), its dome on the origin so that it turns
    about it (yaw=aim): a grey horseshoe base on the ground, armoured flanks, two prongs either
    side of the barrel, a bronze dome, a red light at the back."""
    grey = pal("tur_grey", 0x06, metallic=0.55, roughness=0.4)
    light = pal("tur_light", 0x08, metallic=0.55, roughness=0.35)
    dark = pal("tur_dark", 0x03, metallic=0.4, roughness=0.6)
    bronze = pal("tur_bronze", 0x16, metallic=0.75, roughness=0.3)
    brass = pal("tur_brass", 0x19, metallic=0.75, roughness=0.25)
    red = pal("tur_red", 0x74, metallic=0.0, roughness=0.3, glow=2.0, color=(255, 40, 20))
    rows = sh.grow(TURRET, "b", "k")  # the outline pixels belong to the parts they surround
    x0, y0 = 0.5, -1.5  # moves the sprite's dome centre (-0.5, 1.5) onto the origin
    # The base: everything but the barrel, low, its edge rounded.
    base_rows = ["".join("b" if ch in "bpdrk" else "." for ch in row) for row in rows]
    base_rows = ["".join("." if (r < 6) else ch for ch in row) for r, row in enumerate(base_rows)]
    base = G2.polys(base_rows, "b", smooth=1, epsilon=0.3)
    kit.solid("base", base, lambda x, y, d: 0.6 + 1.6 * round_edge(d, 1.0), 0.0, dark, spacing=0.55, band=1.1,
              coarse=3)
    # The flanks (columns 5-8 and 14-17, rows 11-17) and the back between them.
    flank = [(G2.x(5.2), G2.y(10.9)), (G2.x(9), G2.y(10.9)), (G2.x(9), G2.y(18)), (G2.x(6), G2.y(18)),
             (G2.x(5.2), G2.y(17.2))]
    for side, outline in (("l", flank), ("r", [(-1.0 - x, y) for x, y in reversed(flank)])):
        kit.solid(f"flank_{side}", [outline], lambda x, y, d: 2.0 + 2.6 * round_edge(d, 1.3) - 0.12 * abs(x + 0.5),
                  0.5, light if side == "l" else grey, spacing=0.5, band=1.4)
    back = [(G2.x(8.5), G2.y(14.6)), (G2.x(14.5), G2.y(14.6)), (G2.x(14.5), G2.y(18)), (G2.x(8.5), G2.y(18))]
    kit.solid("back", [back], lambda x, y, d: 2.0 + 1.1 * round_edge(d, 0.8), 0.5, grey, spacing=0.4, band=0.9)
    # The prongs either side of the barrel, sloping down to their tips.
    for side, col in (("l", 8.5), ("r", 13.5)):
        x = G2.x(col + 0.5) if side == "l" else G2.x(col + 0.5)
        kit.lathe(f"prong_{side}", [(G2.y(11.5), 1.2), (G2.y(10), 1.15), (G2.y(7.6), 1.0), (G2.y(7.0), 0.7),
                                    (G2.y(6.7), 0.1)], light if side == "l" else grey, axis="y", at=(x, 2.4),
                  squash=1.1)
    # The dome, its dark collar, the barrel with its brass muzzle.
    kit.lathe("collar", [(1.0, 0.1), (1.0, 2.75), (3.3, 2.75), (3.3, 0.1)], dark, axis="z", at=(-0.5, 1.6), angle=30)
    kit.ellipsoid("dome", (-0.5, 1.6, 3.4), (2.55, 2.45, 2.6), bronze, 24, 12)
    barrel_z = 4.4
    kit.lathe("barrel", [(1.5, 0.75), (G2.y(5), 0.6), (G2.y(5.1), 0.62)], light, axis="y", at=(-0.5, barrel_z),
              segments=14)
    kit.lathe("muzzle", [(G2.y(5.2), 0.66), (G2.y(5.0), 0.72), (G2.y(2.4), 0.72), (G2.y(2.2), 0.45),
                         (G2.y(2.15), 0.1)], brass, axis="y", at=(-0.5, barrel_z), segments=14)
    kit.lathe("mantlet", [(2.6, 0.2), (2.9, 1.05), (4.1, 1.05), (4.4, 0.2)], grey, axis="y", at=(-0.5, barrel_z),
              segments=16)
    # The red light at the back.
    kit.ellipsoid("light", (G2.x(12), G2.y(17.3), 3.05), (0.95, 0.6, 0.45), red, 14, 7)
    kit.transform_all(Matrix.Translation((x0, y0, 0)))


# --- 3 8 / 3 10: the twin claw ship ---------------------------------------------------------------

# Rows of the upper claw's top edge per column of 3 8 (the arm spans that row to row 8; the lower
# claw is its mirror image about row 13).
CLAW_TOP = [7, 6, 6, 5, 5, 4, 4, 4, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 4, 4, 4, 5, 5, 6]
# The flame between the claws: (column, first row, last row) of its pixels.
CLAW_FLAME = [(4, 14, 14), (5, 13, 14), (6, 13, 14), (7, 13, 14), (8, 13, 14), (9, 12, 14), (10, 12, 15),
              (11, 12, 15), (12, 12, 15), (13, 11, 14), (14, 11, 14), (15, 12, 14), (16, 12, 14)]
CLAW_MID_Y = G2.y(13.5)  # the claws' mirror line (between rows 13 and 14 of 3 8: y = 0.5)
CLAW_Z = 4.2


def twin_claw():
    """The left half (3 8): its claws reach left, its hub and half the glowing core are at the right
    edge, where the right half (3 10, the mirror image) goes on."""
    steel = pal("claw_steel", 0x08, metallic=0.45, roughness=0.32)
    light = pal("claw_light", 0x09, metallic=0.6, roughness=0.28)
    dark = pal("claw_dark", 0x03, metallic=0.5, roughness=0.5)
    flame_mats = [pal("claw_flame_" + str(i), 0x70 + i, metallic=0.0, roughness=0.5, glow=0.5 + 0.12 * (i - 4))
                  for i in (4, 5, 7, 9, 11)]
    core = pal("claw_core", 0x77, metallic=0.0, roughness=0.2, glow=2.0, color=(255, 40, 10))
    # The claws: horns along x, their top edge a smooth arc through the sprite's (rows 7 at the tip,
    # 3 in the middle, 6 at the hub), their inner edge row 8; round in section.
    def claw_top(u):  # u: columns from the sprite's left edge
        return 11.0 - 4.0 * ((13 - u) / 13) ** 2 if u < 13 else 11.0 - 3.0 * ((u - 13) / 11) ** 2

    bottom = G2.y(9)
    for side in (1, -1):
        sections = []
        for i in range(31):
            u = 0.25 + 23.75 * (i / 30) ** 0.85
            top = claw_top(u)
            hw = (top - bottom) / 2
            yc = (top + bottom) / 2 - 0.15 * smoothstep(8, 0, u)  # the tip hooks in a little
            if side < 0:
                yc = 2 * CLAW_MID_Y - yc
            hz = min(2.6, 0.62 * hw + 0.5)
            sections.append((G2.x(u), yc, CLAW_Z + (0.25 if side > 0 else -0.1) + 0.2 * hw, hw, hz))
        tip = sections[0]
        kit.section_loft(f"claw{side}", sections, steel, segments=20, power=2.2,
                         start=(G2.x(0) - 0.15, tip[1], tip[2]), end=None, angle=60)
    # The hub: knuckles where the claws meet it and a spine between them, bulging to the right.
    for side in (1, -1):
        y = G2.y(9.6) if side > 0 else 2 * CLAW_MID_Y - G2.y(9.6)
        kit.ellipsoid(f"knuckle{side}", (G2.x(17.5), y, CLAW_Z + 0.6), (3.6, 1.9, 2.6), light, 20, 10)
    spine = kit.catmull([(G2.x(16.5), G2.y(9.5), CLAW_Z + 0.4), (G2.x(19.3), CLAW_MID_Y, CLAW_Z + 0.6),
                         (G2.x(16.5), 2 * CLAW_MID_Y - G2.y(9.5), CLAW_Z + 0.4)], 0.8)
    kit.tube("spine", spine, [1.0] * len(spine), steel, 12, squash=1.3)
    kit.lathe("collar", [(G2.x(17.2), 0.1), (G2.x(17.2), 1.9), (G2.x(18.6), 1.9), (G2.x(18.6), 0.1)], dark,
              axis="x", at=(CLAW_MID_Y + 0.2, CLAW_Z), segments=20, angle=30)
    # The flame between the claws, hottest at the hub.
    sections = []
    for col, r0, r1 in CLAW_FLAME:
        top, bot = G2.y(r0), G2.y(r1 + 1)
        hw = (top - bot) / 2 - 0.1
        sections.append((G2.x(col + 0.5), (top + bot) / 2, CLAW_Z, hw, 0.6 * hw))
    sections = [(x, yc, zc, hw, hz) for x, yc, zc, hw, hz in
                zip(*[[v[i] for v in k.profile([(s_[0],) + s_[1:] for s_ in sections], 0.7)] for i in range(5)])]
    sections.append((G2.x(18.0), CLAW_MID_Y + 0.3, CLAW_Z, 1.1, 0.8))
    flame = kit.section_loft("flame", sections, flame_mats[0], segments=20,
                             start=(G2.x(3.6), sections[0][1], CLAW_Z), end=(G2.x(18.3), CLAW_MID_Y + 0.3, CLAW_Z))
    x0, x1 = G2.x(4), G2.x(15)
    heat = [smoothstep(x0, x1, v.co.x) * 0.7 + 0.3 * max(0.0, 1 - abs(v.co.y - CLAW_MID_Y - 0.4) / 1.6)
            for v in flame.data.vertices]
    kit.band_split(flame, heat, [(-9, flame_mats[0]), (0.3, flame_mats[1]), (0.5, flame_mats[2]),
                                 (0.68, flame_mats[3]), (0.86, flame_mats[4])], smooth_angle=70)
    # The glowing core between the two halves, cut at the sprite's edge.
    core_obj = kit.ellipsoid("core", (12.0, CLAW_MID_Y + 0.5, CLAW_Z + 0.3), (2.4, 2.3, 2.2), core, 24, 12)
    sh.cut_planes([core_obj], [((12.0, 0, 0), (1, 0, 0))])


def twin_claw_left():
    twin_claw()


def twin_claw_right():
    twin_claw()
    kit.mirror_all()


# --- A 237 / 275 (and their mirror images A 7 / 45): the fire flap ---------------------------------

# The flap's face, as the closed frames draw it (A 231 rows 9-27 over A 269 rows 0-18, columns 0-10
# from the hinge out): shades of the fire ramp (palette 0x70 + shade), the hinge knuckles' pixels
# replaced by 6.
FLAP_FACE = """
44444444411
66455556541
66666667763
66888aba964
66abcffca95
66bddffdaa6
69abcdda9b7
6aa999a8ac9
9abaaaaacda
bccccccceeb
ddddeeefffb
bccccccceeb
aaaabcccddb
88888abbcda
7777778abca
66777779aba
66688879aba
666888889a9
665999999a9
667aaaaa9a9
669ccccbab9
669ddddcbc7
46aeeffdcd7
57adeeeecd6
59befffedf6
5abdfffedf6
49abdddddf5
479abccdde5
3678999bdd4
3456789abc4
334679aaac4
6678aaa9ab4
66b799988b3
66634558ac2
66344568c91
6649999b930
35555554200
23222221000
"""
FLAP_TOP, FLAP_BOTTOM = G2.y(9), G2.y(28 + 19)  # y 5 .. -33: rows 9 of A 237 to 18 of A 275
FLAP_HINGE_X, FLAP_HINGE_Z = -11.3, 1.0
# The hinge knuckles (y ranges, in the top sprite's coordinates).
FLAP_KNUCKLES = [(G2.y(10), G2.y(15)), (G2.y(24), G2.y(28 + 3)), (G2.y(28 + 12), G2.y(28 + 17))]


def _flap_field():
    rows = [line for line in FLAP_FACE.strip().split("\n")]
    grid = [[int(ch, 16) for ch in row] for row in rows]

    def shade(x, y):
        """The face's shade at a point of the closed flap (bilinear between pixel centres)."""
        c = x - G2.x(0) - 0.5
        r = FLAP_TOP - y - 0.5
        c0, r0 = math.floor(c), math.floor(r)
        fc, fr = c - c0, r - r0
        total = weight = 0.0
        for rr, cc, wt in ((r0, c0, (1 - fr) * (1 - fc)), (r0, c0 + 1, (1 - fr) * fc), (r0 + 1, c0, fr * (1 - fc)),
                           (r0 + 1, c0 + 1, fr * fc)):
            rr, cc = min(max(rr, 0), len(grid) - 1), min(max(cc, 0), 10)
            total += grid[rr][cc] * wt
            weight += wt
        return total / weight
    return shade


def fire_flap(piece, mirror):
    """The whole flap of two sprites, built closed (lying flat, its fire face up, as A 231 and 269
    draw it), then swung up about its hinge to stand on edge (A 237 and 275, the enemies' first
    frame); cut into the top or bottom sprite's piece."""
    steel = pal("flap_steel", 0x0a, metallic=0.6, roughness=0.3)
    steel_dark = pal("flap_steel_dark", 0x06, metallic=0.55, roughness=0.4)
    fire = [pal(f"flap_fire_{i:x}", 0x70 + i, metallic=0.0, roughness=0.45, glow=g)
            for i, g in ((3, 0.5), (5, 0.8), (8, 1.2), (10, 1.6), (12, 2.0), (14, 2.5))]
    shade = _flap_field()
    half = 0.42  # half the flap's thickness
    rect = [(G2.x(0), FLAP_BOTTOM), (G2.x(11), FLAP_BOTTOM), (G2.x(11), FLAP_TOP), (G2.x(0), FLAP_TOP)]
    flap = kit.solid("flap", [rect], lambda x, y, d: FLAP_HINGE_Z + half * (0.55 + 0.45 * round_edge(d, 0.4)),
                     lambda x, y, d: FLAP_HINGE_Z - half * (0.55 + 0.45 * round_edge(d, 0.4)), fire[0],
                     spacing=0.75)
    # The far edge (the top when it stands) glows darker, as the edge-on frames draw it.
    values = [min(shade(v.co.x, v.co.y), 8.0 if v.co.x > G2.x(10.6) else 99) for v in flap.data.vertices]
    kit.band_split(flap, values, [(-9, fire[0]), (4.5, fire[1]), (7.5, fire[2]), (9.5, fire[3]), (11.5, fire[4]),
                                  (13.5, fire[5])], smooth_angle=50)
    # Swung up about the hinge: the far edge rises, the fire face turns outwards.
    swing = (Matrix.Translation((FLAP_HINGE_X, 0, FLAP_HINGE_Z)) @ Matrix.Rotation(math.radians(-90), 4, "Y") @
             Matrix.Translation((-FLAP_HINGE_X, 0, -FLAP_HINGE_Z)))
    flap.data.transform(swing)
    # The hinge: knuckles round a pin, on a low rail along the ground.
    for i, (y0, y1) in enumerate(FLAP_KNUCKLES):
        kit.lathe(f"knuckle{i}", [(y1, 0.55), (y1 + 0.15, 0.95), (y0 - 0.15, 0.95), (y0, 0.55)], steel, axis="y",
                  at=(FLAP_HINGE_X, FLAP_HINGE_Z), segments=16, angle=40)
        for y in (y0 - 0.35, y1 + 0.35):
            kit.lathe(f"ring{i}_{y}", [(y - 0.12, 0.9), (y - 0.1, 1.0), (y + 0.1, 1.0), (y + 0.12, 0.9)], steel_dark,
                      axis="y", at=(FLAP_HINGE_X, FLAP_HINGE_Z), segments=16, angle=40)
    kit.lathe("pin", [(FLAP_BOTTOM + 0.2, 0.35), (FLAP_BOTTOM + 0.3, 0.45), (FLAP_TOP - 0.3, 0.45),
                      (FLAP_TOP - 0.2, 0.35)], steel_dark, axis="y", at=(FLAP_HINGE_X, FLAP_HINGE_Z), segments=10)
    rail = [(G2.x(0), FLAP_BOTTOM - 0.4), (G2.x(1.2), FLAP_BOTTOM - 0.4), (G2.x(1.2), FLAP_TOP + 0.4),
            (G2.x(0), FLAP_TOP + 0.4)]
    kit.solid("rail", [rail], lambda x, y, d: 0.25 + 0.35 * round_edge(d, 0.3), 0.0, steel_dark, spacing=0.5,
              band=0.4, coarse=3)
    # The piece of this sprite (the bottom one moved up to its own centre).
    objects = kit.meshes()
    kit.bake()
    if piece == "top":
        sh.cut_box(objects, -50, 50, G2.y(28), 50)
    else:
        sh.cut_box(objects, -50, 50, -100, G2.y(28))
        kit.transform_all(Matrix.Translation((0, 28, 0)))
    if mirror:
        kit.mirror_all()


def fire_flap_r_top():
    fire_flap("top", False)


def fire_flap_r_bottom():
    fire_flap("bottom", False)


def fire_flap_l_top():
    fire_flap("top", True)


def fire_flap_l_bottom():
    fire_flap("bottom", True)


# --- Building ------------------------------------------------------------------------------------

E = kit.ENEMIES
MODELS = [
    ("desert_rock_tip", desert_rock_tip, [("3", 180, False)], E),
    ("molten_rock", molten_rock, [("L", 115, False)], E),
    ("dark_ember", dark_ember, [("L", 118, False)], E),
    ("asteroid_lumpy", asteroid_lumpy, [("D", 5, True)], E),
    ("asteroid_turret", asteroid_turret, [("P", 15, True, (-0.5, 1.5))], E),
    ("twin_claw_left", twin_claw_left, [("3", 8, True)], E),
    ("twin_claw_right", twin_claw_right, [("3", 10, True)], E),
    ("fire_flap_r_top", fire_flap_r_top, [("A", 237, True)], E),
    ("fire_flap_r_bottom", fire_flap_r_bottom, [("A", 275, True)], E),
    ("fire_flap_l_top", fire_flap_l_top, [("A", 7, True)], E),
    ("fire_flap_l_bottom", fire_flap_l_bottom, [("A", 45, True)], E),
]

kit.run(MODELS)
