"""BRAINIAC's and GRAVITRON's fleshy stinger (sheet 5 sprite 207, 2x2: a 15 x 27 stinger in the 24 x 28 cell,
columns 5-19 of rows 0-26; not animated; top layer; enemy 642: 24 in BRAINIAC, 3 in GRAVITRON, which send them
down the screen in threes, five ticks apart), polished (2026-10-21; it replaces wave3_l.py's flesh_stinger(), a
lathe with three seams laid on). models.cfg: sprite 5 207 flesh_stinger yaw=0 (unchanged); not origin, so the game
centres it in height. No other sprite has its pixels (mirrored, turned or in other ramps).

As the sprite and its 4x upscale draw it, point down the screen, in the flesh ramp 4 (0x41 the outline, 0x43-0x46
the sheath, 0x48-0x4e the lit flesh): a broad round cap at the back (rows 0-4: a flange, lit along its upper rim,
its underside dark), a bright neck under it (rows 4-6) and a dark groove (row 6); then a fleshy sheath, a collar
(rows 7-9) above an arched opening whose rim runs over the top at row 9.5 and down both sides; in the opening, the
beak of two halves, two bulging lobes split by a dark cleft (column 12, rows 10-16), and under them, its top an arch
tucked under the lobes' rounded ends (row 16), the beak's pointed lower lobe with a ridge down its middle, between
the sheath's sides converging to the point (row 26).

The model: the sheath, the collar, the neck and the cap are one round body turned about the sprite's axis (the
middle of its column 12: x 0.5), its profile from the sprite's outline rows (PROFILE, about a third of a pixel
inside the dark outline pixels); the body inside the opening is the dark of the creases. The three lobes are reliefs
lying in the opening (polish_ring_machine.py's relief(): their tops follow the body's front, rising from below it at
their outlines, so the creases round them are real, to a rounded crown), painted in the sprite's shades along smooth
borders: lighter on their upper left, which the sun lights, darker where they turn away into the creases. Glossy
flesh as BRAINIAC's brains in their clamps (polish_brain_clamp.py, polish_red_link.py): metallic 0.1, roughness
0.24-0.4, glowing a little in its own colours (0.1-0.18), so that the round sides don't read black from the slanted
camera.

Origin at the sprite's centre (pixel 12, 14); +Y up the screen, +Z towards the camera; the body's axis at z = 0.
Points are given as (u, y): u = x - 0.5, across from the axis.

Replaces wave3_l.py's flesh_stinger() (its "# --- 5 207: BRAINIAC's stinger" section: the @model("flesh_stinger",
207) function) and the flesh_stinger line of its docstring; wave3_l_art.py's STINGER is read by nothing: remove it
too. So that they don't overwrite this model.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouette against
enemy_5.png), --preview <prefix> (top and 3/4 views).
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
from polish_ring_machine import ccw, chaikin, relief, round_edge  # noqa: E402
from polish_sphere_nozzle import smoothstep  # noqa: E402

SPRITE = 207
AXIS_X = 0.5


def monotone(xs, ys):
    """A smooth curve through (xs, ys) that never overshoots them (monotone cubic)."""
    n = len(xs)
    d = [(ys[i + 1] - ys[i]) / (xs[i + 1] - xs[i]) for i in range(n - 1)]
    m = [d[0]] + [(d[i - 1] + d[i]) / 2 if d[i - 1] * d[i] > 0 else 0.0 for i in range(1, n - 1)] + [d[-1]]
    for i in range(n - 1):
        if d[i] == 0:
            m[i] = m[i + 1] = 0.0
            continue
        a, b = m[i] / d[i], m[i + 1] / d[i]
        if a * a + b * b > 9:
            t = 3 / math.sqrt(a * a + b * b)
            m[i], m[i + 1] = t * a * d[i], t * b * d[i]

    def f(x):
        x = min(max(x, xs[0]), xs[-1])
        i = max(0, min(n - 2, next((j for j in range(n - 1) if x <= xs[j + 1]), n - 2)))
        h = xs[i + 1] - xs[i]
        t = (x - xs[i]) / h
        return ((2 * t ** 3 - 3 * t ** 2 + 1) * ys[i] + (t ** 3 - 2 * t ** 2 + t) * h * m[i] +
                (-2 * t ** 3 + 3 * t ** 2) * ys[i + 1] + (t ** 3 - t ** 2) * h * m[i + 1])
    return f


# --- The body -----------------------------------------------------------------------------------------------------
# Its radius along y, from the point (row 26) to the cap's top (row 0): the sheath tapering to the point (rows 17-26),
# the beak's halves (rows 12-16, half-width 5.5 with the outline), the collar (rows 7-11, 6.5), the groove (row 6),
# the neck (rows 4-5, 5.5) and the cap (rows 0-4, 7.5; its top edge rounding to row 0's 5.5).
PROFILE = [(-12.95, 0.0), (-12.7, 0.3), (-12.2, 0.62), (-11.5, 1.02), (-10.5, 1.55), (-9.5, 2.05), (-8.5, 2.55),
           (-7.5, 3.05), (-6.5, 3.5), (-5.5, 3.95), (-4.5, 4.4), (-3.5, 4.85), (-2.6, 5.12), (-1.0, 5.24), (0.8, 5.28),
           (1.7, 5.42), (2.3, 5.88), (3.0, 6.12), (4.6, 6.22), (6.4, 6.18), (6.85, 5.8), (7.15, 5.05), (7.45, 4.85),
           (7.75, 5.05), (8.05, 5.32), (8.6, 5.4), (9.2, 5.42), (9.45, 6.1), (9.75, 6.75), (10.2, 7.12), (11.0, 7.3),
           (12.0, 7.3), (12.7, 7.08), (13.2, 6.6), (13.6, 5.9), (13.85, 5.0), (13.97, 3.6), (14.0, 0.0)]
RADIUS = monotone([p[0] for p in PROFILE], [p[1] for p in PROFILE])
Y_TIP, Y_TOP = PROFILE[0][0], PROFILE[-1][0]
# The bands down the body: the cap above CAP_FOOT (its underside where the surface faces down the screen), the
# neck, the groove, the collar; the sheath below.
CAP_FOOT, NECK_FOOT, GROOVE_FOOT = 9.25, 7.62, 6.95
# Round the body: fine over its front (which the cameras see), coarse behind.
ANGLES = [math.pi * j / 28 for j in range(28)] + [math.pi + math.pi * j / 8 for j in range(8)]


def body_z(u, y):
    """The height of the body's front at (u, y)."""
    r = RADIUS(y)
    return math.sqrt(max(r * r - u * u, 0.0))


# --- The opening and the lobes ------------------------------------------------------------------------------------
# The opening in the sheath's front (u, y), its left half from the top of its arch (row 9.5 over the cleft) round
# its left side to the point: the arch, the side past the upper lobe, the junction J where the lower lobe's top
# meets it (row 16.7) and the side converging to the point (row 26.3).
OPENING_LEFT = [(0.0, 4.55), (-1.2, 4.42), (-2.4, 4.08), (-3.45, 3.45), (-4.2, 2.55), (-4.6, 1.4), (-4.68, 0.0),
                (-4.55, -1.4), (-4.15, -2.7), (-3.55, -4.0), (-2.95, -5.5), (-2.35, -7.2), (-1.75, -8.9),
                (-1.15, -10.45), (-0.6, -11.6), (0.0, -12.3)]
J = 8  # the junction's index
CLEFT = 0.12   # half the cleft's width: the upper lobes' inner edges
GAP = 0.16     # between the upper lobes' ends and the lower lobe's top
# The lower lobe's top, an arch under the upper lobes' rounded ends, from the junction to its top (row 15.8).
ARCH = [(-4.15, -2.7), (-3.6, -2.95), (-2.75, -2.9), (-1.85, -2.55), (-0.95, -2.05), (0.0, -1.8)]
LOWER_POINT = -11.85   # the lower lobe's point (row 25.9), inside the body's (row 26.9)


def upper_left_outline():
    """The upper left lobe: from the cleft's top over the arch and down the opening's side to the junction, along
    the lower lobe's top (GAP above it) back to the cleft and up it."""
    side = [p for p in OPENING_LEFT[:J + 1] if p[0] < -0.5]
    end = [(x, y + GAP) for x, y in ARCH[1:-1]]
    return ccw(chaikin([(-CLEFT, 4.4)] + side + end + [(-CLEFT, ARCH[-1][1] + GAP + 0.25)], 2))


def lower_outline():
    """The lower lobe: its top arch from the middle to the junction, down the opening's side to the point (short of
    the body's own), and up the right side."""
    left = [p for p in ARCH[::-1] + OPENING_LEFT[J + 1:-2] if p[0] < 0.0] + [(-0.5, LOWER_POINT + 0.75)]
    return ccw(chaikin([(0.0, ARCH[-1][1])] + left + [(0.0, LOWER_POINT)] + mirrored(left), 2))


RIDGE_U = -0.25
# Heights: the lobes rise from LOBE_SINK below the body's front at their outlines, steeply within LOBE_ROUND, to
# LOBE_RISE above it, and on in a crown CROWN high towards their middles (the upper lobes' at UPPER_MIDDLE, their
# half-sizes UPPER_SIZE; the lower lobe's along its ridge, a little left of its middle).
LOBE_SINK, LOBE_RISE, LOBE_ROUND = 0.55, 0.3, 1.0
UPPER_CROWN, UPPER_MIDDLE, UPPER_SIZE = 1.15, (-2.3, 0.7), (2.7, 4.1)
LOWER_CROWN, RIDGE_RISE, RIDGE_WIDTH = 0.95, 0.32, 0.6
# The colours' borders on the lobes: lit (the upper left, towards the sun) above LIT, dark (turned away) below
# DARK; their creases within EDGE of the outline.
LIT, DARK, EDGE = 0.035, -0.1, 0.3
SUN = Vector((-0.6, 0.6, 1.0)).normalized()   # the game's sun, from above and the top left of the screen
INSET = 0.35   # the body is the creases' dark inside the opening this far in from its outline (under the lobes)


def mirrored(points):
    return [(-x, y) for x, y in reversed(points)]


def closed(left):
    """A symmetric outline from its left half (top to bottom along the left side): counter-clockwise."""
    right = mirrored(left[1:-1])
    return ccw(chaikin(left + right, 2))


def to_model(points):
    return [(u + AXIS_X, y) for u, y in points]


def opening_inset():
    """The opening, INSET in from its outline (where the body is the creases' dark)."""
    import numpy as np
    from polish_ring_machine import Region
    poly = to_model(closed(OPENING_LEFT))
    region = Region([poly])

    def test(x, y):
        p = np.array([[x, y]])
        return bool(region.inside(p)[0]) and float(region.distance(p)[0]) > INSET
    return test


def upper_height(side):
    """The upper lobe's top: the body's front, the rise round its outline and its crown."""
    mu, mv = UPPER_MIDDLE
    hu, hv = UPPER_SIZE

    def h(x, y, d):
        u = x - AXIS_X
        q = ((side * u - mu) / hu) ** 2 + ((y - mv) / hv) ** 2
        crown = UPPER_CROWN * max(0.0, 1.0 - q) ** 0.8
        return body_z(u, y) - LOBE_SINK + (LOBE_SINK + LOBE_RISE) * round_edge(d, LOBE_ROUND) + crown
    return h


def lower_height(ridged=True):
    """The lower lobe's top: the body's front, the rise round its outline, its crown and (ridged) the ridge."""
    def h(x, y, d):
        u = x - AXIS_X
        along = smoothstep(-1.9, -4.2, y) * (1 - smoothstep(-8.5, -11.8, y))
        crown = LOWER_CROWN * math.exp(-((u - RIDGE_U) / 2.1) ** 2) * along
        ridge = RIDGE_RISE * math.exp(-((u - RIDGE_U) / RIDGE_WIDTH) ** 2) * along if ridged else 0.0
        return body_z(u, y) - LOBE_SINK + (LOBE_SINK + LOBE_RISE) * round_edge(d, LOBE_ROUND * 0.8) + crown + ridge
    return h


def light_field(height):
    """How much a relief's top at (x, y) faces the sun more than straight up does (its slope's normal)."""
    def f(x, y, d):
        e = 0.12
        dzx = (height(x + e, y, d) - height(x - e, y, d)) / (2 * e)
        dzy = (height(x, y + e, d) - height(x, y - e, d)) / (2 * e)
        n = Vector((-dzx, -dzy, 1.0)).normalized()
        return n.dot(SUN) - SUN.z
    return f


def lobe(name, poly, height, mats, light=None):
    """A lobe: a relief over poly, its top at height(x, y, d), painted by how its top (or the smoother light(x, y,
    d), for the colours' borders) faces the sun, its crease round the outline dark."""
    lit = light_field(light or height)

    def paint(x, y, d):
        if d < EDGE:
            return "crease"
        v = lit(x, y, d)
        return "lobe_light" if v > LIT else "lobe_dark" if v < DARK else "lobe"

    borders = [(lambda x, y, d: d, EDGE), (lit, LIT), (lit, DARK)]
    obj = relief(name, [poly], height, mats, paint=paint, side="crease", bottom=0.0, spacing=0.36, borders=borders,
                 smooth_angle=70.0)
    return obj


def body(mats):
    """The round body: rings along y about the axis, denser where the profile turns, painted in bands."""
    ys = []
    y = Y_TIP + 0.05
    while y < Y_TOP - 0.02:
        step = 0.45
        if y > 6.6:
            step = 0.24
        elif 1.3 < y < 3.3:
            step = 0.25
        ys.append(y)
        y += step
    ys = sorted(set(ys) | {CAP_FOOT, NECK_FOOT, GROOVE_FOOT, Y_TOP - 0.06, Y_TOP - 0.15, Y_TIP + 0.15})
    rings = []
    for y in ys:
        r = RADIUS(y)
        rings.append([Vector((AXIS_X + r * math.cos(a), y, r * math.sin(a))) for a in ANGLES])
    obj = k.loft("body", rings, None, start_point=(AXIS_X, Y_TIP, 0.0), end_point=(AXIS_X, Y_TOP, 0.0))
    in_opening = opening_inset()
    names = []
    for poly in obj.data.polygons:
        c, n = poly.center, poly.normal
        if c.y > CAP_FOOT:
            key = "cap_under" if n.y < -0.45 else "cap"
        elif c.y > NECK_FOOT:
            key = "neck"
        elif c.y > GROOVE_FOOT:
            key = "groove"
        elif n.z > 0.15 and in_opening(c.x, c.y):
            key = "crease"
        elif c.y > 3.2:
            key = "collar"
        else:
            key = "sheath"
        if key not in names:
            names.append(key)
            obj.data.materials.append(mats[key])
        poly.material_index = names.index(key)
    return k.smooth(obj, 50)


def materials():
    pal = k.level_palette()

    def flesh(name, index, roughness, glow, glow_index=None):
        return k.material("stinger_" + name, palette=index, metallic=0.1, roughness=roughness,
                          emission=pal[glow_index if glow_index is not None else index], emission_strength=glow)
    return {
        "cap": flesh("cap", 0x48, 0.3, 0.16),
        "cap_under": flesh("cap_under", 0x44, 0.35, 0.12),
        "neck": flesh("neck", 0x4b, 0.25, 0.18),
        "groove": flesh("groove", 0x42, 0.4, 0.1),
        "collar": flesh("collar", 0x46, 0.32, 0.14),
        "sheath": flesh("sheath", 0x45, 0.32, 0.14),
        "crease": flesh("crease", 0x42, 0.4, 0.1),
        "lobe": flesh("lobe", 0x48, 0.26, 0.16),
        "lobe_light": flesh("lobe_light", 0x4a, 0.24, 0.18),
        "lobe_dark": flesh("lobe_dark", 0x46, 0.3, 0.14),
    }


def triangulate(objects):
    """Every face split into triangles (the same split every run, the custom normals kept), so that the export
    doesn't split them itself (polish_k_pod.py's)."""
    for obj in objects:
        mod = obj.modifiers.new("triangulate", "TRIANGULATE")
        mod.quad_method = "BEAUTY"
        mod.ngon_method = "BEAUTY"
        mod.min_vertices = 4
        mod.keep_custom_normals = True
        mk.apply(obj)


def build_stinger():
    mats = materials()
    body(mats)
    left = upper_left_outline()
    lobe("lobe_l", to_model(left), upper_height(1), mats)
    lobe("lobe_r", to_model(ccw(mirrored(left))), upper_height(-1), mats)
    lobe("lobe_low", to_model(lower_outline()), lower_height(), mats, light=lower_height(False))
    return mk.meshes()


def build():
    options = k.args()
    k.reset()
    parts = build_stinger()
    triangulate(parts)
    if "check" in options:
        k.check_silhouette(os.path.join(options["check"], "enemy_5.png"), SPRITE)
    bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
    mk.report("flesh_stinger", parts, os.path.join(mk.outdir(options), "flesh_stinger.glb"))
    if "preview" in options:
        mk.preview(options["preview"] + "flesh_stinger", parts, distance=0.62)


if __name__ == "__main__":
    build()
