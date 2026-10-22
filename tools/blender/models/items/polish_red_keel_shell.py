"""The red armour shell (coins sheet sprite 279, 2x2: a 23 x 28 shell in the 24 x 28 cell; one frame): enemy 560, the ship
that brings armour, polished (2026-10-22, round 34; it replaces wave3_ai_items.py's red_keel_shell(): a lathed bar and
keel with two ribbed spheres for pods). models.cfg: sprite coins 279 red_keel_shell yaw=0 (unchanged); the game centres
it in height on its layer.

What it is (src/tyrian2.c, JE_main): whenever a player's armour is under 6, every 500 game frames the game sends one down
the screen (JE_newEnemy(50, 560): the top layer; armour 5 (4 left), worth 100; falling fast and slowing, then on again:
ymove 5, ycaccel -8), and shot it leaves an armour pick-up (561-563); so it shows in any level of any episode (the
catalogue: "any", sky). No other enemy shows coins 279, and no sprite is its pixels mirrored, turned or in other ramps.

As the sprite and its 4x upscale draw it (columns and rows of the cell; symmetric about column 12, x 0.5, but its
light): a shield-shaped shell in a black outline (0x01): across its top a thick rolled bar of ramp 4's reds (columns 2-22
of rows 2-8, lit at its upper left: 0x4e-0x4f at columns 5-6), a gold lip showing over it (ramp 1, columns 6-17 of rows
0-1); from the bar's middle a broad keel down to the shell's point (columns 8-16 of rows 9-22, narrowing to column 12
of row 27), a groove down its middle (0x43-0x44 at column 12 of rows 11-15) between two lit ridges, its right side
darker; and under the bar either side of the keel an olive-gold pod (ramp 1, columns 4-7 and 17-20 of rows 8-21): a
small upper bulb and a longer lower one with a waist between (row 12), each with a bright glint (0x1b at column 5 of
row 10; 0x1c-0x1e at column 6 of rows 15-16; the right pod's mirrored).

Built for the game's camera in the item family's way (polish_fruit_items.py: glossy parts painted in bands by the light
they get, glowing a little in their own colours so that the slanted camera doesn't show the reds brown), modelled about
the shell's middle plane (z 0: the game centres it in height) in the picture's plane, then sheared along the camera's
line of sight (y - z tan 20, as polish_carrot.py), so that the camera sees each part where the sprite draws it:
- the bar: turned about an axis across the screen (BAR: its radius along it, rounded at its ends), a little flattened,
  its ends bowing a little down the screen (BAR_BOW);
- the gold lip: a gold rod behind the bar's top;
- the keel: lofted down the screen through superelliptic sections (KEEL: half-width, top and bottom), its top two ridges
  either side of a groove that fades out down the keel (GROOVE);
- the pods: two glossy olive-gold bulbs each (POD), a small light-gold glass lens on each bulb where the sprite draws its
  glint, glowing a little;
- under them a dark red back plate (HULL) along the shield's outline, filling the gaps between the parts.
Reds 0x44-0x4f, golds 0x12-0x1a and 0x1e by the light (the sun from the top left), the reds glowing 0.06-0.2.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera; origin at the
sprite's centre (pixel 12, 14): column c is x = c + 0.5 - 12, row r is y = 13.5 - r. Every mesh is triangulated
(polish_k_pod.triangulate) and the parts joined into one mesh; no random numbers, no booleans.

Replaces wave3_ai_items.py's red_keel_shell() (its section "# --- Coins 279: the red armour shell": RED_PLATE and the
@kit.model("red_keel_shell", ...) function, and the red shell's words in its docstring) and wave3_ai_art.py's RED_PLATE
(nothing else reads it).

Options after "--": --outdir <dir> (default assets/models/items), --check <sheets dir> (the silhouette in the camera's
view against coins.png's 279), --preview <prefix>.
"""
import math
import os
import sys

import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(HERE, "..", "enemies"))
sys.path.insert(0, HERE)
import polish_item_kit as kit  # noqa: E402
from polish_item_kit import k  # noqa: E402
from polish_deli_boss import join  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402
from polish_launched_flames import lit, vertex_normals  # noqa: E402
from polish_orb_red import band_split  # noqa: E402
from polish_sphere_nozzle import smoothstep  # noqa: E402

SPRITE = 279
TAN_T = math.tan(math.radians(20.0))
LIGHT = Vector((-0.6, 0.6, 1.0)).normalized()   # towards the game's sun
AXIS_X = 0.5


def P(c, r, z=0.0):
    return Vector((c + 0.5 - 12.0, 13.5 - r, z))


# The bar: its axis (row, z), its radius up the screen and its height (z), its ends (x, two thirds into the outline),
# how far in from them it rounds off.
BAR = (5.0, 0.6, 3.72, 3.0, (-10.67, 11.67), 1.25)
BAR_BOW = 0.55                  # its ends that much lower down the screen than its middle (a rolled edge bowing)
# The gold lip: from column to column, its row, z, radius.
LIP = (6.35, 16.65, 0.55, 1.2, 0.95)
# The keel: sections (row, half-width, top z, bottom z) from under the bar to the point; its top's groove: depth, half-
# width (pixels), and from where to where (rows) it shows.
KEEL = [(6.0, 4.35, 2.4, -1.8), (8.0, 4.5, 2.75, -2.0), (12.0, 4.5, 2.8, -2.1), (17.0, 4.5, 2.5, -2.0),
        (21.5, 4.45, 2.0, -1.8), (23.0, 4.1, 1.75, -1.6), (24.4, 3.3, 1.45, -1.3), (25.6, 2.3, 1.1, -1.0),
        (26.6, 1.35, 0.8, -0.7), (27.2, 0.6, 0.5, -0.4), (27.62, 0.05, 0.2, -0.1)]
GROOVE = (0.8, 0.6, 9.5, 20.5)
# The pods (the left one; the right one its mirror image about the axis): bulbs (column, row, z of the middle; radii),
# and the lenses where the sprite draws their glints (column, row, radius).
POD = [((6.0, 10.2, 0.2), (2.2, 2.45, 1.85)), ((6.05, 16.2, 0.1), (2.4, 4.35, 2.0))]
LENSES = [(5.2, 10.0, 0.5), (6.1, 15.6, 0.72)]
# The back plate: (row, half-width) along the shield's outline, a little inside it; its top and bottom z.
HULL = [(0.6, 5.6), (1.3, 9.0), (2.2, 10.6), (3.0, 11.0), (8.3, 11.0), (9.2, 10.1), (10.0, 9.2), (19.6, 9.2),
        (20.4, 8.1), (21.3, 7.1), (22.3, 5.9), (23.3, 4.2), (25.0, 3.0), (26.2, 2.0), (27.3, 0.9), (27.6, 0.1)]
HULL_Z = (0.4, -2.2)

# Colours: (lowest light value, palette index, glow).
REDS = [(-99.0, 0x43, 0.06), (0.3, 0x45, 0.09), (0.5, 0x47, 0.12), (0.68, 0x49, 0.15), (0.84, 0x4b, 0.18),
        (0.96, 0x4e, 0.2)]
GOLDS = [(-99.0, 0x12, 0.0), (0.32, 0x15, 0.0), (0.55, 0x17, 0.0), (0.76, 0x1a, 0.0)]


def materials():
    m = {}
    for _, index, glow in REDS:
        m[index] = lit(f"shell_red_{index:x}", index, glow, roughness=0.26, metallic=0.15)
    for _, index, _ in GOLDS:
        m[index] = k.material(f"shell_gold_{index:x}", palette=index, metallic=0.55, roughness=0.3)
    m["dark"] = lit("shell_dark", 0x42, 0.04, roughness=0.4, metallic=0.2)
    m["lens"] = lit("shell_lens", 0x1c, 0.16, roughness=0.08, metallic=0.1)
    return m


def light(n):
    sun = max(0.0, n.dot(LIGHT))
    return 0.55 * n.z + 0.35 * sun + 0.1 * sun ** 8


def interp(table, t):
    if t <= table[0][0]:
        return table[0][1]
    for (t0, v0), (t1, v1) in zip(table, table[1:]):
        if t <= t1:
            return v0 + (v1 - v0) * (t - t0) / (t1 - t0)
    return table[-1][1]


def bar(m):
    row, z, ry, rz, (x0, x1), round_in = BAR
    y = P(0, row).y
    # the profile along x: (x, radius share), rounded over round_in at both ends
    xs = [x0 + (x1 - x0) * i / 40 for i in range(41)]
    rings = []
    for x in xs[1:-1]:
        d = min(x - x0, x1 - x)
        share = math.sqrt(max(0.0, 1.0 - (1.0 - min(d, round_in) / round_in) ** 2))
        pts = []
        yc = y - BAR_BOW * ((x - AXIS_X) / (0.5 * (x1 - x0))) ** 2
        for j in range(24):
            a = 2 * math.pi * j / 24
            pts.append(Vector((x, yc + ry * share * math.cos(a), z + rz * share * math.sin(a))))
        rings.append(pts)
    obj = k.loft("bar", rings, m[0x47], start_point=(x0, y - BAR_BOW, z), end_point=(x1, y - BAR_BOW, z))
    k.recalc_normals(obj)
    return obj


def lip(m):
    c0, c1, r, z, rad = LIP
    a, b = P(c0, r, z), P(c1, r, z)
    rings = []
    for i in range(1, 18):
        t = i / 18
        p = a.lerp(b, t)
        share = math.sqrt(max(0.0, 1.0 - (2 * t - 1) ** 8))
        rings.append([p + Vector((0.0, math.cos(2 * math.pi * j / 10), math.sin(2 * math.pi * j / 10))) * rad * share
                      for j in range(10)])
    obj = k.loft("lip", rings, m[0x17], start_point=a, end_point=b)
    k.recalc_normals(obj)
    return obj


def keel(m):
    table = sorted(KEEL)
    rows = [table[0][0] + (table[-1][0] - table[0][0]) * i / 40 for i in range(41)]
    depth, gw, g0, g1 = GROOVE
    rings = []
    for r in reversed(rows[:-1]):        # (from the point up the screen)
        hw = interp([(row, w) for row, w, _, _ in table], r)
        top = interp([(row, t) for row, _, t, _ in table], r)
        bottom = interp([(row, b) for row, _, _, b in table], r)
        fade = smoothstep(g0 - 1.5, g0, r) * smoothstep(g1 + 2.5, g1, r)
        y = P(0, r).y
        pts = []
        for j in range(28):
            a = 2 * math.pi * j / 28
            c, s = math.cos(a), math.sin(a)
            u = math.copysign(abs(c) ** (2 / 2.4), c)
            v = math.copysign(abs(s) ** (2 / 2.4), s)
            x = AXIS_X + u * hw
            zz = v * (top if s >= 0 else -bottom)
            if s > 0:
                zz -= depth * fade * math.exp(-((u * hw) / gw) ** 2) * v
            pts.append(Vector((x, y, zz)))
        rings.append(pts)
    end = table[-1]
    obj = k.loft("keel", rings, m[0x47], start_point=(AXIS_X, P(0, end[0]).y, 0.0),
                 end_point=(AXIS_X, P(0, table[0][0]).y, 0.6))
    k.recalc_normals(obj)
    return obj


def pod(m, side):
    out = []
    for i, ((c, r, z), radii) in enumerate(POD):
        if side > 0:
            c = 24.0 - c
        bulb = k.ellipsoid(f"pod{i}{'lr'[side > 0]}", tuple(P(c, r, z)), radii, m[0x15], segments=20, rings_count=12)
        out.append(bulb)
    for i, (c, r, rad) in enumerate(LENSES):
        if side > 0:
            c = 24.0 - c
        bulb_c, bulb_r = POD[0] if i == 0 else POD[1]
        bc = P(24.0 - bulb_c[0] if side > 0 else bulb_c[0], bulb_c[1], bulb_c[2])
        p = P(c, r)
        q = 1.0 - ((p.x - bc.x) / bulb_r[0]) ** 2 - ((p.y - bc.y) / bulb_r[1]) ** 2
        z = bc.z + bulb_r[2] * math.sqrt(max(q, 0.0))
        lens = k.ellipsoid(f"lens{i}{'lr'[side > 0]}", (p.x, p.y, z - 0.14), (rad, rad, rad * 0.4), m["lens"],
                           segments=12, rings_count=6)
        out.append(lens)
    return out


def hull(m):
    table = sorted(HULL)
    top, bottom = HULL_Z
    rows = [table[0][0] + (table[-1][0] - table[0][0]) * i / 30 for i in range(31)]
    rings = []
    for r in reversed(rows[1:-1]):
        hw = interp(table, r)
        rings.append(k.ring(P(0, r).y, hw, (top - bottom) / 2, 24, z=(top + bottom) / 2, x=AXIS_X, power=3.0))
    obj = k.loft("hull", rings, m["dark"], start_point=(AXIS_X, P(0, table[-1][0]).y, (top + bottom) / 2),
                 end_point=(AXIS_X, P(0, table[0][0]).y, (top + bottom) / 2))
    return obj


def paint(obj, table, m):
    values = [light(n) for n in vertex_normals(obj)]
    band_split(obj, values, [(lo, m[index]) for lo, index, _ in table])
    return obj


def shear(objects):
    for obj in objects:
        for v in obj.data.vertices:
            v.co.y -= v.co.z * TAN_T
        obj.data.update()


def build_model():
    k.reset()
    m = materials()
    reds = [bar(m), keel(m)]
    golds = [lip(m)] + pod(m, -1) + pod(m, 1)
    back = hull(m)
    parts = reds + golds + [back]
    shear(parts)
    for obj in reds:
        paint(obj, REDS, m)
    for obj in golds:
        if not obj.name.startswith("lens"):
            paint(obj, GOLDS, m)
    for obj in parts:
        k.smooth(obj, 60)
    triangulate(parts)
    return [join(parts, "red_keel_shell")]


def build():
    opts = kit.options()
    objects = build_model()
    bpy.context.view_layer.update()
    if "check" in opts:
        seen = []
        for obj in objects:
            copy = obj.copy()
            copy.data = obj.data.copy()
            bpy.context.scene.collection.objects.link(copy)
            for v in copy.data.vertices:
                v.co.y += v.co.z * TAN_T
            seen.append(copy)
        bpy.context.view_layer.update()
        kit.compare("red_keel_shell (coins %d) in the camera's view" % SPRITE, kit.coverage(seen, 24, 28),
                    kit.sprite_mask(opts["check"], SPRITE, True))
        for copy in seen:
            mesh = copy.data
            bpy.data.objects.remove(copy)
            bpy.data.meshes.remove(mesh)
    bpy.context.scene.view_settings.view_transform = "Standard"
    kit.report("red_keel_shell", objects, os.path.join(kit.outdir(opts), "red_keel_shell.glb"))
    if "preview" in opts:
        kit.preview(opts["preview"] + "red_keel_shell", objects, (24, 28), scale=16)


if __name__ == "__main__":
    build()
