"""SAWBLADES' carrot (sheet 8 sprite 129, 2x2: 24 x 28 pixels; one frame), polished (2026-10-22, round 34; it replaces
wave3_y.py's sawblades_carrot(), a lathed root with rings, a heightfield hollow and three lofted leaves).
models.cfg: sprite 8 129 sawblades_carrot yaw=0 (unchanged); the game centres it in height on its layer.

What it is (tools/content/tyrevents.py): SAWBLADES' hidden carrots. Event 51 (a custom top enemy: enemy 0's data with
sprite 129 of sheet 8, armour 10) puts one on the top layer at t80 (x 220); each later one only if the one before it was
shot (events 60 / 61: special flags 1-6), at t580 (x 160), t1180 (160), t1880 (240), t2480 (160), t3880 (90) and t4180
(160), and the last drops the HOT DOG (enemy 801, coins 92). They don't move (they scroll with the top layer). No other
enemy shows 8 129, and no enemy sprite is its pixels mirrored, turned or in other ramps; but it is the player's
SuperCarrot (ship 2, ships sheet sprite 119) flipped upside down, a pixel to the right: rows reversed, its tip down
the screen (ships/carrot.glb is that ship's own model, an old one: not touched here).

As the sprite draws it (the ship's 4x upscale, flipped, is its upscale): an orange carrot, its tip down the screen
(column 12 of row 27), widest at rows 11-14 (columns 6-18 with the outline), its round shoulder at row 9, glossy in
the fire ramp 7 (0x75 at its edges, 0x79-0x7b, a lit stripe down its left middle, 0x7d at rows 12-13 and 19-21); a
round canopy in its upper middle (columns 10-14 of rows 14-18): a dark rim (0xb0) round its top and right, its glass
brown (0xb4-0xb6) and lighter to the lower left (0xb8-0xba), a bright glint in its middle (0x7e); on top a tuft of three
green leaves (ramp 12, 0xc0-0xcb) from a short stalk (columns 11-13 of rows 7-8): the left one a narrow blade up to the
upper left (its tip at column 6 of row 1), the middle one broad and straight up (row 0), the right one short, out to the
right (columns 13-16 of rows 3-5); the dark red outline (0x70) round all.

Built in the fruit's family (polish_fruit_items.py: glossy skins painted in bands by the light they get, glowing a little
in their own colours so that the slanted camera doesn't show them brown; leaves as lens-shaped tubes,
polish_torm_beetle.tube): the root lathed about its axis (a little flattened, ROOT: its radius along it, from the sprite's
outline), its skin rippled by shallow rings (RINGS, as a carrot's), cut into bands of ramp 7 by the light (the glare
0x7d where the sun strikes it), glowing 0.1-0.26; the canopy a glass dome sunk into the root's top, in a dark rim, its
glass brown and lighter to the lower left (0xb5, 0xb9), a glint in its middle (0x7e, glowing); the stalk and three
leaves in ramp 12 by the light (0xc2-0xc8), glowing faintly. Modelled about the root's axis (z 0 its middle: the game centres the
model in height) in the picture's plane, then sheared along the game camera's line of sight (y - z tan 20, as
polish_ixm_spider.py), so that the canopy and the leaves on its top show where the sprite draws them.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera; origin at the
sprite's centre (pixel 12, 14): column c is x = c + 0.5 - 12, row r is y = 13.5 - r. The root's axis is the sprite's
column 12 (x 0.5). Every mesh is triangulated (polish_k_pod.triangulate) and joined; no random numbers, no booleans.

Replaces wave3_y.py (all of it: the carrot was its last model; nothing imports it) and wave3_y_art.py's CARROT.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouette in the camera's
view against enemy_8.png's 129), --preview <prefix>.
"""
import math
import os
import sys

import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
import polish_machine_kit as mk  # noqa: E402
from polish_deli_boss import join  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402
from polish_launched_flames import lit, vertex_normals  # noqa: E402
from polish_orb_red import band_split  # noqa: E402
from polish_sphere_nozzle import smoothstep  # noqa: E402
from polish_torm_beetle import tube  # noqa: E402

SPRITE = 129
TAN_T = math.tan(math.radians(20.0))
LIGHT = Vector((-0.6, 0.6, 1.0)).normalized()   # towards the game's sun
AXIS_X = 0.5


def P(c, r, z=0.0):
    return Vector((c + 0.5 - 12.0, 13.5 - r, z))


# The root: (row, radius) from its shoulder down to its tip (the sprite's outline, two thirds into its black), its
# section SQUASH as high as wide; shallow rings round it (rows), RING_DEPTH deep (a share of the radius), RING_W wide.
ROOT = [(8.6, 0.02), (8.65, 2.4), (8.85, 3.7), (9.1, 4.3), (9.6, 4.9), (10.2, 5.45), (10.8, 5.9), (11.5, 6.2),
        (12.5, 6.3), (13.5, 6.25), (14.0, 6.1), (15.0, 5.85), (16.0, 5.6), (17.0, 5.3), (18.0, 4.95), (19.0, 4.65),
        (20.0, 4.3), (21.0, 3.95), (22.0, 3.45), (23.0, 2.9), (24.0, 2.4), (25.0, 1.85), (26.0, 1.3), (27.0, 0.65),
        (27.6, 0.02)]
SQUASH = 0.8
RINGS = [10.4, 13.0, 19.4, 21.6, 23.6, 25.4]
RING_DEPTH, RING_W = 0.018, 0.3
# The canopy: its middle (column, row), radius, how high its glass stands over the skin; its rim.
CANOPY = (12.0, 16.0, 2.35, 0.75)
RIM = 0.32
# The leaves: stations (column, row, z over the root's axis, half-width, half-height) from the stalk to the tip.
LEAVES = [
    ("leaf_l", [(11.0, 7.3, 0.9, 0.75, 0.3), (9.5, 5.7, 2.0, 1.35, 0.32), (7.75, 3.9, 2.4, 1.3, 0.3),
                (6.75, 2.3, 2.1, 0.95, 0.24), (6.15, 0.8, 1.6, 0.14, 0.1)]),
    ("leaf_m", [(11.9, 7.4, 1.0, 0.85, 0.32), (11.75, 5.4, 2.4, 1.8, 0.36), (11.7, 3.4, 2.9, 1.85, 0.34),
                (11.6, 1.7, 2.7, 1.2, 0.25), (11.5, 0.15, 2.2, 0.14, 0.1)]),
    ("leaf_r", [(12.5, 7.0, 0.9, 0.7, 0.3), (13.6, 5.5, 1.9, 1.5, 0.32), (14.8, 4.3, 2.1, 1.45, 0.3),
                (15.9, 3.6, 1.8, 0.14, 0.1)]),
]
STALK = [(12.0, 9.9, 0.0, 1.25, 1.0), (12.0, 8.4, 0.5, 1.2, 0.95), (12.0, 7.3, 0.95, 0.95, 0.75)]

# Colours: the skin's bands by the light (lowest value, palette index, glow); the leaves'; the canopy.
SKIN = [(-99.0, 0x75, 0.1), (0.25, 0x77, 0.13), (0.45, 0x79, 0.16), (0.62, 0x7a, 0.19), (0.76, 0x7b, 0.22),
        (0.88, 0x7d, 0.26)]
LEAF = [(-99.0, 0xc2, 0.06), (0.35, 0xc4, 0.08), (0.6, 0xc6, 0.1), (0.82, 0xc8, 0.12)]


def materials():
    m = {}
    for _, index, glow in SKIN:
        m[index] = lit(f"carrot_skin_{index:x}", index, glow, roughness=0.3)
    for _, index, glow in LEAF:
        m[index] = lit(f"carrot_leaf_{index:x}", index, glow, roughness=0.45)
    m["rim"] = k.material("carrot_canopy_rim", palette=0xb2, metallic=0.4, roughness=0.35)
    m["glass"] = k.material("carrot_canopy_glass", palette=0xb5, metallic=0.1, roughness=0.08)
    m["glass_lit"] = k.material("carrot_canopy_glass_lit", palette=0xb9, metallic=0.1, roughness=0.08)
    m["glint"] = lit("carrot_canopy_glint", 0x7e, 0.45, roughness=0.1)
    return m


def light(n):
    sun = max(0.0, n.dot(LIGHT))
    return 0.55 * n.z + 0.35 * sun + 0.1 * sun ** 8


def radius(y):
    """The root's radius at y (0 beyond its ends), its rings pressed in."""
    rows = [(13.5 - r, rad) for r, rad in ROOT]
    rows.sort()
    if y <= rows[0][0] or y >= rows[-1][0]:
        return 0.0
    pts = k.profile(rows, step=0.05)
    best = min(pts, key=lambda p: abs(p[0] - y))
    groove = sum(math.exp(-((y - (13.5 - r)) / RING_W) ** 2) for r in RINGS)
    return best[1] * (1.0 - RING_DEPTH * groove)


def skin_top(x, y):
    """The height of the root's top at (x, y) (its axis at z 0)."""
    r = radius(y)
    u = (x - AXIS_X) / r if r > 0 else 2.0
    return SQUASH * r * math.sqrt(max(0.0, 1.0 - u * u))


def root(m):
    rows = sorted((13.5 - r, rad) for r, rad in ROOT)
    ys = [rows[0][0] + (rows[-1][0] - rows[0][0]) * i / 70 for i in range(1, 70)]
    rings = [k.ring(y, radius(y), radius(y) * SQUASH, 32, x=AXIS_X) for y in ys]
    obj = k.loft("root", rings, m[0x79], start_point=(AXIS_X, rows[0][0], 0.0), end_point=(AXIS_X, rows[-1][0], 0.0))
    return obj


def canopy(m):
    c, r, rad, height = CANOPY
    centre = P(c, r)
    base = skin_top(centre.x, centre.y)
    rings = []
    for i in range(1, 12):
        a = math.pi / 2 * i / 12
        rr = rad * math.sin(a)
        ring = []
        for j in range(28):
            phi = 2 * math.pi * j / 28
            x, y = centre.x + rr * math.cos(phi), centre.y + rr * math.sin(phi)
            z = skin_top(x, y) + height * math.cos(a) - 0.25 * (1 - math.cos(a))
            ring.append(Vector((x, y, z)))
        rings.append(ring)
    glass = k.loft("canopy", list(reversed(rings)), m["glass"], start_point=(centre.x, centre.y, base - 0.6),
                   end_point=(centre.x, centre.y, base + height))
    k.recalc_normals(glass)
    # The rim round it: a ring laid on the skin.
    pts = []
    for j in range(36):
        phi = 2 * math.pi * j / 36
        x, y = centre.x + (rad + 0.1) * math.cos(phi), centre.y + (rad + 0.1) * math.sin(phi)
        pts.append(Vector((x, y, skin_top(x, y) + 0.05)))
    rim_rings = []
    for i, p in enumerate(pts):
        t = (pts[(i + 1) % len(pts)] - pts[i - 1]).normalized()
        out = Vector((p.x - centre.x, p.y - centre.y, 0.0)).normalized()
        up = t.cross(out).normalized()
        if up.z < 0:
            up = -up
        rim_rings.append([p + (out * math.cos(2 * math.pi * q / 8) + up * math.sin(2 * math.pi * q / 8)) * RIM
                          for q in range(8)])
    faces, verts = [], []
    for ring in rim_rings:
        verts += [tuple(v) for v in ring]
    n = len(rim_rings)
    for i in range(n):
        for q in range(8):
            a, b = i * 8 + q, i * 8 + (q + 1) % 8
            c2, d = ((i + 1) % n) * 8 + (q + 1) % 8, ((i + 1) % n) * 8 + q
            faces.append((a, b, c2, d))
    rim = k.mesh_object("canopy_rim", verts, faces, m["rim"])
    k.recalc_normals(rim)
    return glass, rim


def paint(obj, bands_table, m):
    values = [light(n) for n in vertex_normals(obj)]
    band_split(obj, values, [(lo, m[index]) for lo, index, _ in bands_table])
    return obj


def paint_canopy(glass, m):
    c, r, rad, _ = CANOPY
    centre = P(c, r)

    def value(co, n):
        # lighter to the lower left (as the sprite: the glass lit through), the glint in the middle where it faces up
        d = Vector((co.x - centre.x, co.y - centre.y))
        if d.length < 0.55 and n.z > 0.9:
            return 3.0
        return 1.0 + 0.6 * (-d.x - d.y) / rad
    values = [value(v.co, n) for v, n in zip(glass.data.vertices, vertex_normals(glass))]
    band_split(glass, values, [(-99.0, m["glass"]), (1.45, m["glass_lit"]), (2.5, m["glint"])])
    return glass


def shear(objects):
    for obj in objects:
        for v in obj.data.vertices:
            v.co.y -= v.co.z * TAN_T
        obj.data.update()


def build_model():
    k.reset()
    m = materials()
    skin = root(m)
    glass, rim = canopy(m)
    leaves = [tube(name, [tuple(P(c, r, z)) + (hw, hh, 1.2) for c, r, z, hw, hh in st], m[0xc4], segments=12)
              for name, st in LEAVES]
    stalk = tube("stalk", [tuple(P(c, r, z)) + (hw, hh, 2.0) for c, r, z, hw, hh in STALK], m[0xc4], segments=14)
    parts = [skin, glass, rim, stalk] + leaves
    shear(parts)
    paint(skin, SKIN, m)
    paint_canopy(glass, m)
    for leaf in leaves + [stalk]:
        paint(leaf, LEAF, m)
    for obj in parts:
        k.smooth(obj, 60 if obj is not rim else 80)
    triangulate(parts)
    return [join(parts, "sawblades_carrot")]


def build():
    options = k.args()
    objects = build_model()
    bpy.context.view_layer.update()
    if "check" in options:
        seen = []
        for obj in objects:
            copy = obj.copy()
            copy.data = obj.data.copy()
            bpy.context.scene.collection.objects.link(copy)
            for v in copy.data.vertices:
                v.co.y += v.co.z * TAN_T
            seen.append(copy)
        bpy.context.view_layer.update()
        mk.compare("sawblades_carrot (8 %d) in the camera's view" % SPRITE, mk.coverage(seen, 24, 28),
                   k.sprite_mask(os.path.join(options["check"], "enemy_8.png"), SPRITE))
        for copy in seen:
            mesh = copy.data
            bpy.data.objects.remove(copy)
            bpy.data.meshes.remove(mesh)
    bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
    mk.report("sawblades_carrot", objects, os.path.join(mk.outdir(options), "sawblades_carrot.glb"))
    if "preview" in options:
        mk.preview(options["preview"] + "sawblades_carrot", objects)


if __name__ == "__main__":
    build()
