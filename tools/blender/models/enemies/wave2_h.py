"""Enemies of wave 2, batch H, modelled as their sprites look (models.cfg: yaw=0 unless noted). (GYGES' bronze
ingot, H 93: polish_yuanbao.py; the molten rock ball, L 115 and 3 134: polish_molten_rock.py; the rock arch's
nub, 3 180: polish_rock_arch.py; the fire flaps, A 237 and others: polish_fire_gate.py.)

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
from mathutils import Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wave2_h_kit as kit  # noqa: E402
from wave2_h_kit import G2, k, pal, sh, smoothstep  # noqa: E402

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


# --- Building ------------------------------------------------------------------------------------

E = kit.ENEMIES
MODELS = [
    ("asteroid_lumpy", asteroid_lumpy, [("D", 5, True)], E),
    ("twin_claw_left", twin_claw_left, [("3", 8, True)], E),
    ("twin_claw_right", twin_claw_right, [("3", 10, True)], E),
]

kit.run(MODELS)
