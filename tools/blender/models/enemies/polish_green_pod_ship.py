"""TORM's green ship with a red crest and red pods at its sides (sheet J sprite 117, 2x2: 24 x 28 pixels; enemies 760
and 761, armour 40, worth 50, one frame, not animated: TORM's event 6 puts them on the ground layer at t1300 (760) and
t2600 ... 3340 (761, seven times), moving down the screen (ymove 1)), polished (2026-10-22, round 33; it replaces
wave3_m.py's green_pod_ship(), a hull grown from the sprite's green pixels with a tube collar, a sphere crest and lathed
pods). models.cfg: model green_pod_ship enemies/green_pod_ship.glb and sprite j 117 green_pod_ship yaw=0 (the lines as
they are: centred in height, no origin; the game rests it on the ground). No other enemy shows J 117 (catalog.json,
launched ones too); it is no other sprite's pixels mirrored, turned or in other ramps (the green scarab, J 131, and the
green skiff are other drawings); no episode 6 level places it (GREY MOON takes TORM's boss only).

As the sprite and its 4x upscale draw it (columns and rows of the 24 x 28 sprite; symmetric about column 12, lit from
the upper left; the greens of ramp 2, the reds of ramp 7): along its top a red crest (columns 6-17 of rows 0-1, 0x72-
0x76) with two orange lights in it (columns 8-10 and 14-15 of row 1: 0x79-0x7c); under it a broad green collar right
across the ship (columns 2-22 of rows 2-8), its upper left lit along a ridge (column 6: 0x2c-0x2f), its right end lit
along its edge (columns 21-22); from it the hull (columns 8-16 of rows 7-21) narrowing to a point down the screen
(rows 22-26), a light spine down its middle (column 12: 0x2a-0x2d at rows 5-12), its left flank lit (0x25-0x2a), its
right one in shade (0x20-0x24); and at the hull's sides two glossy red pods (columns 4-7 and 17-20 of rows 8-21, 0x71-
0x76), two lights glowing in each: a small one high up (row 10: 0x7a, 0x7b) and a longer one lower down (rows 13-17:
0x78-0x7c, a white-hot 0xff at row 16 in the left one), the right pod's inner side black (0xf0) at its ends, where it
meets the hull.

Built as such a craft (polish_green_scarab.py's way and family: lofted shells, glossy red pods, glowing lamps; painted
as polish_torm_beetle.py paints its greens, in bands of the light each face gets): the hull lofted from rounded
sections along y (HULL: half-widths as the sprite's outline, its top highest under the collar and falling to the tip,
a spine raised along its middle, flat underneath); the collar a rounded plate lofted along x (COLLAR: its plan the
sprite's, arched along its length and rounded over its edges), two low ribs along its top where the sprite lights its
ridges; the crest a red bar lying along the collar's top edge; the pods round tubes along y (POD), their ends rounded;
the lights glowing lenses on the pods and the crest (emission 0.45-0.65, the game's bloom adds), the lower ones long
slits, the left one's hottest spot 0x7e. Painted in bands of the light (LIGHT, the game's sun from the upper left: a
value from how squarely a face meets it and how far it faces up, cut along smooth contours, polish_orb_red.band_split):
greens 0x23 0x25 0x27 0x29 0x2b and a 0x2d highlight, a shade or two lighter than the sprite's as the slanted camera
sees them darker; reds 0x73 0x75 0x77 (glossy, the lightest glowing a little, 0.12: the sprite's pods are bright).

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up from its underside (z 0); origin at
the sprite's centre (pixel corner 12, 14): column c's middle is x = c + 0.5 - 12, row r's is y = 13.5 - r; the ship's
axis at x 0.5 (column 12).

Replaces wave3_m.py's green_pod_ship (its section "J 117: the green pod ship": green_pod_ship() and its @model
registration, the empty "J 131: the green scarab" heading above it, greens(), the green_pod_ship bullet of its
docstring), the last model wave3_m.py builds: delete wave3_m.py (nothing imports it); wave3_m_art.py's J117 (read only
by it). wave3_m_kit.py stays (wave3_m_shell.py uses it).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouette from above
against J 117's pixels), --preview <prefix> (top and 3/4 views).
"""
import math
import os
import sys

import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k  # noqa: E402
from polish_deli_boss import join, drop_unused  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402
from polish_orb_red import band_split, smoothstep  # noqa: E402

LIGHT = Vector((-0.6, 0.6, 1.0)).normalized()     # towards the game's sun (polish_torm_beetle's)
AXIS = 0.5                                         # column 12's middle

# The hull: (y, half-width, top height) from under the collar down to its tip.
HULL = [(7.6, 4.7, 4.9), (5.0, 4.75, 4.85), (2.0, 4.75, 4.7), (-1.0, 4.75, 4.5), (-4.0, 4.7, 4.25), (-6.5, 4.65, 4.0),
        (-8.0, 4.45, 3.8), (-9.2, 3.9, 3.5), (-10.3, 3.35, 3.2), (-11.3, 2.7, 2.9), (-12.2, 1.85, 2.55),
        (-12.75, 1.1, 2.2), (-13.05, 0.35, 1.8)]
SPINE = 0.7                                       # the spine's rise along the hull's middle
GROOVES = (-2.3, 2.3)                              # the grooves either side of it (out from the axis)
# The collar: (x, back y, front y, top) along it from its left end to its right (the plan of columns 2-22, rows 2-8).
COLLAR = [(-10.4, 10.6, 6.0, 4.7), (-9.8, 11.7, 5.3, 5.3), (-8.6, 12.2, 4.9, 5.7), (-6.0, 12.4, 5.1, 6.0),
          (-3.0, 12.45, 5.5, 6.2), (0.5, 12.5, 5.7, 6.3), (4.0, 12.45, 5.5, 6.2), (7.0, 12.4, 5.1, 6.0),
          (9.6, 12.2, 4.9, 5.7), (10.8, 11.7, 5.3, 5.3), (11.4, 10.6, 6.0, 4.7)]
COLLAR_BOTTOM = 2.3
RIBS = [-5.5, 6.5]                                 # the low ribs along its top (column 6 and its mirror)
CREST = dict(x0=-5.0, x1=6.0, y=12.85, z=5.9, r=1.15)
CREST_LIGHTS = [(-2.5, 0.85), (3.4, 0.7)]          # x, radius along x (columns 8-10, 14-15)
# The pods: x, (y, radius) along them from the top down; the height of their axis.
POD_X = (-5.45, 6.45)
POD = [(6.2, 0.4), (5.6, 1.4), (4.4, 2.0), (2.5, 2.2), (-2.0, 2.25), (-5.5, 2.15), (-7.0, 1.7), (-7.8, 0.95),
       (-8.15, 0.3)]
POD_Z = 2.45
POD_SQUASH = 1.1                                   # taller than wide
# The pods' lights: (y, half-length along y, half-width), the upper small one and the lower slit; their x offsets
# from the pod's axis (towards the ship's side as the sprite draws them).
POD_LIGHTS = [(3.5, 0.85, 0.72), (-1.6, 2.4, 0.95)]
LIGHT_OFFSET = {(-5.45, 0): -0.75, (-5.45, 1): -0.1, (6.45, 0): 0.75, (6.45, 1): 0.45}


def materials():
    pal = k.level_palette()

    def mat(name, index, metallic=0.2, roughness=0.3, glow=0.0, glow_index=None):
        return k.material(name, palette=index, metallic=metallic, roughness=roughness,
                          emission=pal[glow_index if glow_index is not None else index] if glow > 0 else None,
                          emission_strength=glow)
    m = {i: mat("podship_green", i) for i in (0x23, 0x25, 0x27, 0x29, 0x2b, 0x2d)}
    m.update({i: mat("podship_red", i, 0.3, 0.26) for i in (0x73, 0x75)})
    m[0x77] = mat("podship_red", 0x77, 0.3, 0.24, 0.12)       # the pods' and the crest's lit faces glow a little
    m["lamp"] = mat("podship_lamp", 0x7a, 0.0, 0.2, 0.45)
    m["lamp_core"] = mat("podship_lamp_core", 0x7c, 0.0, 0.18, 0.55)
    m["lamp_hot"] = mat("podship_lamp_hot", 0x7e, 0.0, 0.15, 0.65)
    return m


GREEN_BANDS = [(-99.0, 0x23), (3.8, 0x25), (4.9, 0x27), (5.9, 0x29), (6.8, 0x2b), (7.7, 0x2d)]
RED_BANDS = [(-99.0, 0x73), (4.4, 0x75), (6.0, 0x77)]


def vertex_normals(obj):
    mesh = obj.data
    normals = [Vector() for _ in mesh.vertices]
    for poly in mesh.polygons:
        for vi in poly.vertices:
            normals[vi] += poly.normal * poly.area
    return [n.normalized() for n in normals]


def paint_bands(obj, m, bands, base, extra=None, b=2.0):
    """polish_torm_beetle's light_value: base where a face looks straight up, more towards the sun, less away and down;
    `extra(co, n)` adds to it."""
    vals = []
    for v, n in zip(obj.data.vertices, vertex_normals(obj)):
        val = base + 3.0 * (n.dot(LIGHT) - LIGHT.z) + b * (n.z - 1.0)
        if extra is not None:
            val += extra(v.co, n)
        vals.append(val)
    band_split(obj, vals, [(lo, m[i]) for lo, i in bands])
    k.smooth(obj, 50)


def at_y(table, y, col):
    for a, b in zip(table, table[1:]):
        if b[0] <= y <= a[0]:
            t = (y - a[0]) / (b[0] - a[0])
            t = (1 - math.cos(math.pi * t)) / 2
            return a[col] + (b[col] - a[col]) * t
    return table[0][col] if y > table[0][0] else table[-1][col]


# --- The parts ---------------------------------------------------------------------------------------------------

def hull(m):
    rings = []
    y_top, y_tip = HULL[0][0], HULL[-1][0]
    n = 21
    for i in range(n):
        t = i / (n - 1)
        y = y_tip + (y_top - y_tip) * (t ** 1.4)      # denser towards the tip
        hw = at_y(HULL, y, 1)
        top = at_y(HULL, y, 2)
        rings.append(k.ring(y, hw, top, 28, z=0.0, x=AXIS, top=1.0, bottom=0.0001, power=2.5, crest=SPINE))
    obj = k.loft("hull", rings, m[0x27], start_point=(AXIS, y_tip - 0.15, 0.6), end_point=(AXIS, y_top, 2.0))
    k.smooth(obj, 50)

    def spine(co, nn):
        return 1.2 * math.exp(-((co.x - AXIS) / 0.8) ** 2) * smoothstep(0.0, 3.0, co.z)
    paint_bands(obj, m, GREEN_BANDS, 6.3, spine, b=1.2)
    parts = [obj]
    # Two shallow grooves down it either side of the spine (the upscale's dark slots, the sprite's columns 10 and 14).
    hit = mk.surface([obj])
    for i, dx in enumerate(GROOVES):
        pts, ups = [], []
        for j in range(10):
            y = 4.6 - 13.0 * j / 9
            h = hit(AXIS + dx * min(1.0, at_y(HULL, y, 1) / 4.75), y)
            if h is not None:
                pts.append(h[0] + h[1] * -0.12)
                ups.append(h[1])
        groove = mk.bar("groove%d" % i, pts, ups, 0.38, 0.1, 0.2, m[0x23], 8, 2.4)
        k.smooth(groove, 50)
        parts.append(groove)
    return parts


def collar(m):
    """The collar: sections across it (y, z) lofted along x, each a rounded slab between its back and front edges."""
    rings = []
    xs = [COLLAR[0][0] + (COLLAR[-1][0] - COLLAR[0][0]) * i / 28 for i in range(29)]

    def at_x(x, col):
        for a, b in zip(COLLAR, COLLAR[1:]):
            if a[0] <= x <= b[0]:
                t = (x - a[0]) / (b[0] - a[0])
                t = (1 - math.cos(math.pi * t)) / 2
                return a[col] + (b[col] - a[col]) * t
        return COLLAR[0][col]
    for x in xs:
        yb, yf, top = at_x(x, 1), at_x(x, 2), at_x(x, 3)
        cy, hy = (yb + yf) / 2, (yb - yf) / 2
        zc = (top + COLLAR_BOTTOM) / 2
        hz = (top - COLLAR_BOTTOM) / 2
        ring = []
        for j in range(22):
            a = 2 * math.pi * j / 22
            c, s = math.cos(a), math.sin(a)
            py = math.copysign(abs(c) ** (2 / 3.2), c) * hy
            pz = math.copysign(abs(s) ** (2 / 2.6), s) * hz
            ring.append(Vector((x, cy + py, zc + pz)))
        rings.append(ring)
    first, last = rings[0], rings[-1]
    obj = k.loft("collar", rings, m[0x27], start_point=tuple(sum(first, Vector()) / len(first) - Vector((0.5, 0, 0))),
                 end_point=tuple(sum(last, Vector()) / len(last) + Vector((0.5, 0, 0))))
    k.smooth(obj, 50)
    paint_bands(obj, m, GREEN_BANDS, 6.3)
    parts = [obj]
    # The ribs along its top: low welts where the sprite lights its ridges.
    hit = mk.surface([obj])
    for i, x in enumerate(RIBS):
        pts, ups = [], []
        for j in range(9):
            y = 11.9 - 5.0 * j / 8
            h = hit(x, y)
            if h is not None:
                pts.append(h[0] + Vector((0.0, 0.0, -0.05)))
                ups.append(h[1])
        rib = mk.bar("rib%d" % i, pts, ups, 0.5, 0.42, 0.25, m[0x29], 10, 2.4)
        k.smooth(rib, 50)
        paint_bands(rib, m, GREEN_BANDS, 6.6)
        parts.append(rib)
    # The spine continued over it, from the hull's up to the crest (column 12: 0x2a-0x2d at rows 5-10).
    pts, ups = [], []
    for j in range(9):
        y = 6.2 + (12.0 - 6.2) * j / 8
        h = hit(AXIS, y)
        if h is not None:
            pts.append(h[0] + Vector((0.0, 0.0, -0.05)))
            ups.append(h[1])
    welt = mk.bar("collar_spine", pts, ups, 0.7, 0.45, 0.25, m[0x2b], 10, 2.4)
    k.smooth(welt, 50)
    paint_bands(welt, m, GREEN_BANDS, 7.0)
    parts.append(welt)
    return parts


def crest(m):
    c = CREST
    n = 16
    pts = [Vector((c["x0"] + (c["x1"] - c["x0"]) * i / n, c["y"], c["z"])) for i in range(n + 1)]
    radii = [c["r"] * (0.55 + 0.45 * math.sin(math.pi * min(1.0, 4 * i / n, 4 * (n - i) / n) / 2))
             for i in range(n + 1)]
    obj = mk.tube("crest", pts, c["r"], m[0x75], 20, radii=radii)
    k.smooth(obj, 50)
    paint_bands(obj, m, RED_BANDS, 5.2)
    parts = [obj]
    for i, (x, rx) in enumerate(CREST_LIGHTS):
        lamp = mk.ball("crest_light%d" % i, (x, c["y"] - 0.25, c["z"] + c["r"] * 0.7), (rx, 0.75, 0.55),
                       m["lamp"], 18, 8)
        mk.paint(lamp, lambda co, nn: m["lamp_core"] if nn.z > 0.8 else None)
        parts.append(lamp)
    return parts


def pods(m):
    parts = []
    for px in POD_X:
        pts = [(px, y, POD_Z, r) for y, r in POD]
        pod = mk.smooth_tube("pod%+.0f" % px, pts, m[0x75], 20)
        for v in pod.data.vertices:              # taller than wide
            v.co.z = POD_Z + (v.co.z - POD_Z) * POD_SQUASH
        pod.data.update()
        k.smooth(pod, 50)
        paint_bands(pod, m, RED_BANDS, 6.6, b=1.2)
        parts.append(pod)
        hit = mk.surface([pod])
        for i, (ly, hl, hw) in enumerate(POD_LIGHTS):
            lx = px + LIGHT_OFFSET[(px, i)]
            h = hit(lx, ly)
            if h is None:
                continue
            p, nrm = h
            lamp = mk.ball("pod_light%+.0f_%d" % (px, i), tuple(p - nrm * 0.35), (hw, hl, 0.55), m["lamp"], 20, 10)
            hot = "lamp_hot" if (px < 0 and i == 1) else "lamp_core"

            def pick(co, nn, ly=ly, hl=hl, hot=hot):
                d = abs(co.y - (ly - 0.35 * hl)) / hl
                if nn.z > 0.55 and d < 0.45:
                    return m[hot]
                if nn.z > 0.3 and d < 0.8:
                    return m["lamp_core"]
                return None
            mk.paint(lamp, pick)
            parts.append(lamp)
    return parts


def build():
    options = k.args()
    k.reset()
    m = materials()
    parts = hull(m)
    parts += collar(m)
    parts += crest(m)
    parts += pods(m)
    for obj in parts:
        mk.apply(obj)
    bpy.context.view_layer.update()
    drop_unused(parts)
    triangulate(parts)
    if "check" in options:
        sheet = os.path.join(options["check"], "enemy_J.png")
        mk.compare("green_pod_ship (J 117)", mk.coverage(parts, 24, 28), k.sprite_mask(sheet, 117))
    parts = [join(parts, "green_pod_ship")]
    parts[0].data.name = "green_pod_ship"
    bpy.context.scene.view_settings.view_transform = "Standard"   # previews in the game's colours
    mk.report("green_pod_ship", parts, os.path.join(mk.outdir(options), "green_pod_ship.glb"))
    if "preview" in options:
        mk.preview(options["preview"] + "green_pod_ship", parts, size=(24, 28), scale=16, distance=0.7)


if __name__ == "__main__":
    build()
