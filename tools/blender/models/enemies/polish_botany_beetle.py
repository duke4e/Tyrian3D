"""BOTANY B's blue beetle (sheet 0 sprite 229, 2x2: a 16 x 18 beetle in the 24 x 28 cell; enemy 821 on the ground of
BOTANY B, 24 of them; its animation 229 231 231 233 233 233 231 231 231 229), polished (2026-10-21; it replaces
wave3_ai.py's botany_beetle(), two wing cases of reliefs with a tube for a tail). models.cfg: sprite 0 229
botany_beetle yaw=0 (glow optional, see the report). No other enemy shows these three sprites; they are no other
sprites' pixels mirrored or in other ramps (only each other: 231 and 233 light the streaks on the cases' lower edges,
71/72/74 in 229, 73/74/76 in 231, 75/79/78 in 233, and the blue next to them; the chevron is the same in all three),
so one model serves every frame, its marks lit throughout.

As the sprite and its 4x upscales draw it (columns and rows of the cell; the steel blues of ramp 3, lit from the
upper left; symmetric about the line between columns 11 and 12, x = 0): two wing cases folded side by side, each
rounded at its top into a bump (columns 8-10 and 13-15 of row 7), a notch between the bumps (columns 11-12 of row
8), the cases' inner edges meeting along a dark groove (columns 11-12 of rows 9-13); each case broad at its shoulder
(out to columns 4 and 19 of rows 11-16) with a ridge along it, the lightest steel (3c-3e): near its inner edge down
the upper case (column 9, 14 of rows 8-14), then, past a fold across its outer part (row 14), out in the middle of
the narrower lower case (column 7, 16 of rows 15-19), which runs down beside the tail to a blunt tip (columns 6-7,
16-17 of row 23). Between the cases' lower ends, apart from them by dark gaps (columns 9 and 14 of rows 15-22), the
narrow tail (columns 10-13 of rows 14-22, its tip at row 23), lit on its back (3a-3d) and marked with a glowing red
chevron pointing down the screen (columns 10-13 of rows 18-20: 73 round a hot middle, 79 at column 12 of row 19, 74
77 at its point). A red streak glows along each case's lower end (column 8 of row 20 to column 6 of row 22 and its
mirror image), brightening through the frames.

Built as such a beetle on the ground, as BOTANY's other armoured creatures (polish_botany_eye_pod.py,
polish_botany_stone.py): each wing case one solid over its plan whose top is two plates joined by a smooth maximum,
the fold a crease between them: the upper plate's crest near its inner edge, falling steeply into the groove and
broadly to the outer edge, the lower plate's crest along its middle, a rounded rib along each crest (the sprite's
ridge) with a shallow trough beside it, both plates rounded down to the outline; the tail a rounded vault between the
cases' lower ends, low in the groove at the top; a dark floor under the gaps. The solids are polish_ring_machine's
relief() drawn over a grid of our own (grid_relief()): rows across the plan whose points crowd in at the edges and
at the crest, so that the grid's lines follow the ribs and their light runs smooth along them. The steel is painted
in the sprite's blues by how far each face faces the camera (and a little the sun), the ribs' tops lighter, cut into
bands along smooth contours, a shade lighter than the sprite's (the slanted camera sees them darker); the chevron is
inlaid in the tail's back and the streaks in the cases' lower ends, bands of the sprite's reds by the distance from
their hot middles, glowing in their own colours (emission 0.3-0.55: the game's bloom adds). The model carries a speck
at PIN_Z (a triangle a thousandth of a pixel across, invisible), so the game, which centres a model in height on the
ground enemies' layer (4) and lifts it to 0.3 when it would reach lower, puts the beetle on the ground (as
polish_botany_stone.py does).

Origin at the sprite's centre (pixel 12, 14): column c is x = c + 0.5 - 12, row r is y = 13.5 - r; +Y up the screen,
+Z up from the ground (z = 0). The right case is the left one's plan and top mirrored, each painted by its own light.

Replaces wave3_ai.py's botany_beetle() (its @kit.model("botany_beetle", ...) function, BEETLE, BEETLE_PAINT and
wing_pixel(), and steel() and shade_by_slope(), which only it used: with them gone nothing is left in wave3_ai.py, so
it can be deleted; nothing imports it) and wave3_ai_art.py's BEETLE and BEETLE_233 (nothing else reads them).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouette against
enemy_0.png's 229), --preview <prefix>.
"""
import math
import os
import sys

import bmesh
import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
import polish_machine_kit as mk  # noqa: E402
from polish_ring_machine import Region, ccw, relief, round_edge  # noqa: E402
from polish_sphere_nozzle import smoothstep, split_along  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402

# The left wing case's plan (x, y): its outline traced round the sprite's pixels (their dark outline mostly inside),
# from the notch round the top bump, down the outer edge to the tip and back up beside the tail and the groove.
CASE = [(-1.0, 6.45), (-1.45, 6.9), (-2.4, 7.0), (-3.4, 6.92), (-4.3, 6.45), (-5.25, 5.55), (-6.25, 4.55),
        (-7.15, 3.5), (-7.8, 2.4), (-7.85, 0.0), (-7.8, -2.55), (-7.25, -3.35), (-6.9, -4.3), (-6.9, -9.3),
        (-6.45, -10.45), (-5.6, -10.9), (-4.65, -10.8), (-3.9, -10.05), (-3.2, -9.2), (-2.75, -8.25), (-2.75, -2.0),
        (-2.35, -1.2), (-1.55, -0.4), (-0.85, 0.3), (-0.8, 5.6)]
EDGE = 0.6             # the cases' tops round down to their outline over this
# The upper plate: its crest (x) and inner edge, its height along the crest at heights y ((y, z) ascending), the end
# of the plate (y; it falls away under it), how high its sides stay at the outer edge and at the inner one (fractions
# of the crest's); along its crest a rib (RIB: height, half-width), the sprite's ridge.
UPPER_CREST, UPPER_INNER = -2.55, -0.8
UPPER_HEIGHT = [(-1.6, 4.0), (-0.6, 4.45), (1.0, 4.85), (3.5, 4.95), (5.5, 4.65), (7.0, 3.9)]
UPPER_END = (-2.2, -1.2)
UPPER_SIDES = (0.4, 0.8)
# The lower plate: its crest from (x, y) to (x, y), its height from the fold to the tip, its sides at the edges.
LOWER_CREST = ((-4.4, -0.8), (-5.1, -9.4))
LOWER_HEIGHT = (3.95, 2.95)
LOWER_SIDES = (0.5, 0.55)
LOWER_EDGES = (-6.9, -2.75)
RIB = ((0.85, 0.8), (0.7, 0.75))    # the upper plate's and the lower one's
TROUGH = (0.22, 1.35, 0.55)         # a shallow trough along the ribs' outer sides: depth, distance, half-width
FOLD = 0.3             # how softly the plates meet (a smooth maximum: the crease of the fold)
# The grid the cases' and the tail's tops are drawn on: rows this far apart, points across each row from the outer
# edge to the crest and from it to the inner edge.
ROW_STEP = 0.45
CASE_SAMPLES = (10, 5)
TAIL_SAMPLES = (5, 5)
# The tail between the cases' lower ends: its half-width and top along it ((y, half-width, z) descending); its back
# is a rounded vault (its sides at FULLNESS of its top).
TAIL = [(6.05, 0.7, 1.5), (1.0, 0.8, 1.6), (0.2, 1.1, 2.4), (-0.6, 1.75, 3.7), (-1.5, 2.2, 4.4), (-3.0, 2.35, 4.75),
        (-5.0, 2.3, 4.7), (-6.5, 2.05, 4.3), (-7.6, 1.7, 3.7), (-8.6, 1.2, 3.0), (-9.4, 0.7, 2.2), (-9.95, 0.15, 1.2)]
TAIL_EDGE, FULLNESS = 0.8, 0.62
# The chevron in the tail's back: a triangle pointing down the screen less a notch at its top; its hot middle and the
# reds out from it ((distance, palette index, emission)).
CHEVRON = [(-1.95, -4.05), (1.95, -4.05), (0.0, -7.05)]
CHEVRON_NOTCH = [(-0.75, -4.05), (0.75, -4.05), (0.0, -5.05)]
CHEVRON_HOT = (0.25, -5.65)
CHEVRON_REDS = [(0.55, 0x79, 0.55), (1.05, 0x77, 0.45), (1.6, 0x75, 0.38), (99.0, 0x73, 0.3)]
INLAY = 0.12           # how much the red stands out of the steel
# The streak along the left case's lower end: from its inner end to its outer end, its half-width; the reds along
# it ((fraction along, palette index)).
STREAK = ((-3.2, -6.55), (-5.75, -8.95), 0.34)
STREAK_REDS = [(0.45, 0x73), (99.0, 0x75)]
# The steel's shades by the light a face gets (mostly how far it faces the camera, a little how far it faces the
# sun), the ribs' tops lighter (CREST_LIGHT within CREST_WIDTH of their lines, as the sprite's ridges of 3c-3e), the
# tail's spine a little (SPINE_LIGHT), the groove at the top between the cases darker (GROOVE_SHADE above GROOVE_Y).
SUN = Vector((-0.6, 0.6, 1.0)).normalized()
STEEL = ((0.45, 0.61, 0.82), (0x38, 0x3b, 0x3c, 0x3e))
CREST_LIGHT, CREST_WIDTH = 0.18, 0.85
SPINE_LIGHT = 0.12
GROOVE_SHADE, GROOVE_Y = 0.35, (-1.6, 0.2)
FLOOR = ([(-3.3, 6.2), (3.3, 6.2), (3.4, -8.6), (2.2, -9.3), (0.0, -9.5), (-2.2, -9.3), (-3.4, -8.6)], 1.3)
PIN_Z = 7.6


def materials():
    m = {"floor": k.material("beetle_floor", palette=0x31, metallic=0.2, roughness=0.6)}
    for index in STEEL[1]:
        m[index] = k.material(f"beetle_steel_{index:x}", palette=index, metallic=0.15,
                              roughness=0.42 if index < 0x38 else 0.3 if index < 0x3c else 0.22)
    glow = k.level_palette()
    for _, index, strength in CHEVRON_REDS:
        m[index] = k.material(f"beetle_red_{index:x}", palette=index, metallic=0.0, roughness=0.25,
                              emission=glow[index], emission_strength=strength)
    return m


def steel_key(light):
    return STEEL[1][sum(light > b for b in STEEL[0])]


def interp(points, t):
    """Linear through (t, value) points (ascending t), held at the ends."""
    if t <= points[0][0]:
        return points[0][1]
    for (t0, v0), (t1, v1) in zip(points, points[1:]):
        if t <= t1:
            return v0 + (v1 - v0) * (t - t0) / (t1 - t0)
    return points[-1][1]


def smax(a, b, r):
    h = min(1.0, max(0.0, 0.5 + 0.5 * (a - b) / r))
    return b + (a - b) * h + r * h * (1 - h)


# --- Solids over a grid of rows ------------------------------------------------------------------------------------

def row_span(poly, y):
    """Where the line across the screen at y enters and leaves the polygon (x)."""
    xs = []
    for (x0, y0), (x1, y1) in zip(poly, poly[1:] + poly[:1]):
        if (y0 - y) * (y1 - y) <= 0 and y0 != y1:
            xs.append(x0 + (x1 - x0) * (y - y0) / (y1 - y0))
    return min(xs), max(xs)


def spread(a, b, count):
    """count + 1 points from a to b, a little closer together at both ends."""
    return [a + (b - a) * (0.55 * i / count + 0.45 * (0.5 - 0.5 * math.cos(math.pi * i / count)))
            for i in range(count + 1)]


def grid_rows(poly, step, crest, outer_n, inner_n):
    """Rows of points across a plan from its top to its bottom, step apart, each from its left end to its right end
    through the crest (crest(y): its x), closer together at the ends and at the crest: a grid whose lines follow the
    crest, so that a narrow rib along it is drawn smooth."""
    top, bottom = max(p[1] for p in poly), min(p[1] for p in poly)
    count = max(2, int(round((top - bottom) / step)))
    rows = []
    for j in range(count + 1):
        y = top - 0.03 - (top - bottom - 0.06) * j / count
        lo, hi = row_span(poly, y)
        c = min(max(crest(y), lo + 0.25 * (hi - lo)), hi - 0.25 * (hi - lo))
        rows.append([(x, y) for x in spread(lo, c, outer_n) + spread(c, hi, inner_n)[1:]])
    return rows


def grid_relief(name, rows, top, keys, paint, borders, side, smooth_angle=80.0):
    """A solid over the grid of rows (polish_ring_machine.relief() over a grid of our own): its top at top(x, y, d),
    d the distance to the outline (the rows' ends), the borders [(field(x, y, d), threshold)] cut into it first so that
    colours change along smooth lines, faces named by paint(x, y, d), short walls (side) down to the ground; no
    underside (it is never seen)."""
    outline = [r[0] for r in rows] + [r[-1] for r in reversed(rows)]
    region = Region([ccw(outline)])
    bm = bmesh.new()
    grid = [[bm.verts.new((x, y, 0.0)) for x, y in row] for row in rows]
    for a, b in zip(grid, grid[1:]):
        for i in range(len(a) - 1):
            for tri in ((a[i], b[i], b[i + 1]), (a[i], b[i + 1], a[i + 1])):
                p, q, r = (v.co for v in tri)
                if (q - p).cross(r - p).z > 1e-7:
                    bm.faces.new(tri)
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=1e-5)
    for v in [v for v in bm.verts if not v.link_faces]:
        bm.verts.remove(v)
    distance = {}

    def dist(v):
        if v not in distance:
            distance[v] = float(region.distance([(v.co.x, v.co.y)])[0])
        return distance[v]

    on_outline = {v for e in bm.edges if len(e.link_faces) == 1 for v in e.verts}
    for field, threshold in borders:
        values = {v: field(v.co.x, v.co.y, dist(v)) for v in bm.verts}
        for v in split_along(bm, values, threshold):
            if any(len(e.link_faces) == 1 for e in v.link_edges):
                on_outline.add(v)
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    face_keys = {}
    for f in bm.faces:
        c = f.calc_center_median()
        d = sum(0.0 if v in on_outline else dist(v) for v in f.verts) / len(f.verts)
        face_keys[f] = paint(c.x, c.y, d)
    for v in bm.verts:
        v.co.z = top(v.co.x, v.co.y, 0.0 if v in on_outline else dist(v))
    rim = [e for e in bm.edges if len(e.link_faces) == 1]
    lower = {}
    for e in rim:
        for v in e.verts:
            if v not in lower:
                lower[v] = bm.verts.new((v.co.x, v.co.y, 0.0))
    for e in rim:
        a, b = e.verts
        face_keys[bm.faces.new([b, a, lower[a], lower[b]])] = side
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mesh = bpy.data.meshes.new(name)
    names = []
    for f in bm.faces:
        if face_keys[f] not in names:
            names.append(face_keys[f])
    for key in names:
        mesh.materials.append(keys[key])
    for f in bm.faces:
        f.material_index = names.index(face_keys[f])
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    return k.smooth(obj, smooth_angle)


# --- The wing cases ---------------------------------------------------------------------------------------------

def outer_edge(y):
    """The left case's outer edge (x) at height y, from its plan."""
    return interp([(-9.3, -6.9), (-4.3, -6.9), (-3.35, -7.25), (-2.55, -7.8), (0.0, -7.85), (2.4, -7.8), (3.5, -7.15),
                   (4.55, -6.25), (5.55, -5.25), (6.45, -4.3), (7.0, -3.0)], y)


def ridge(dx, rib):
    """A rib along a crest (dx from it; negative: its outer side) with a shallow trough beside it."""
    height, width = rib
    depth, at, half = TROUGH
    return height * math.exp(-(dx / width) ** 2) - depth * math.exp(-((dx + at) / half) ** 2)


def upper_plate(x, y):
    end = smoothstep(UPPER_END[0], UPPER_END[1], y)
    h = interp(UPPER_HEIGHT, y) * end
    if x <= UPPER_CREST:
        t = min(1.0, (UPPER_CREST - x) / max(0.5, UPPER_CREST - outer_edge(y)))
        z = h * (1.0 - (1.0 - UPPER_SIDES[0]) * t ** 1.25)
    else:
        t = min(1.0, (x - UPPER_CREST) / (UPPER_INNER - UPPER_CREST))
        z = h * (1.0 - (1.0 - UPPER_SIDES[1]) * t ** 1.6)
    return z + ridge(x - UPPER_CREST, RIB[0]) * end * smoothstep(7.2, 5.6, y)


def lower_plate(x, y):
    (x0, y0), (x1, y1) = LOWER_CREST
    f = min(1.0, max(0.0, (y - y0) / (y1 - y0)))
    crest = x0 + (x1 - x0) * f
    end = smoothstep(1.2, -0.6, y)
    h = (LOWER_HEIGHT[0] + (LOWER_HEIGHT[1] - LOWER_HEIGHT[0]) * f) * end
    if x <= crest:
        t = min(1.0, (crest - x) / (crest - LOWER_EDGES[0]))
        z = h * (1.0 - (1.0 - LOWER_SIDES[0]) * t ** 1.6)
    else:
        t = min(1.0, (x - crest) / (LOWER_EDGES[1] - crest))
        z = h * (1.0 - (1.0 - LOWER_SIDES[1]) * t ** 1.6)
    return z + ridge(x - crest, RIB[1]) * end * smoothstep(-10.4, -8.6, y)


def streak_t(x, y):
    """How far along the streak (0-1) the point's nearest point on it lies, and the distance to it."""
    (ax, ay), (bx, by), _ = STREAK
    dx, dy = bx - ax, by - ay
    t = max(0.0, min(1.0, ((x - ax) * dx + (y - ay) * dy) / (dx * dx + dy * dy)))
    return t, math.hypot(x - (ax + dx * t), y - (ay + dy * t))


def streak_field(x, y):
    """Negative inside the streak (its ends rounded)."""
    _, d = streak_t(x, y)
    return d - STREAK[2]


def case_top(x, y, d):
    z = smax(upper_plate(x, y), lower_plate(x, y), FOLD)
    if streak_field(x, y) < 0.3:
        z += INLAY * smoothstep(0.3, -0.1, streak_field(x, y))
    return max(0.25, z * round_edge(d, EDGE))


def light_of(top, region, x, y):
    """The light a top face gets at (x, y): from the top's slopes (finite differences)."""
    e = 0.12
    z = []
    for px, py in ((x + e, y), (x - e, y), (x, y + e), (x, y - e)):
        d = float(region.distance([(px, py)])[0]) if region.inside([(px, py)])[0] else 0.0
        z.append(top(px, py, d))
    n = Vector((-(z[0] - z[1]) / (2 * e), -(z[2] - z[3]) / (2 * e), 1.0)).normalized()
    return 0.76 * n.z - 0.02 + 0.12 * (n.dot(SUN) - 0.6)


def crest_x(y):
    """The left case's crest at y: the upper plate's above the fold, the lower plate's below it."""
    (x0, y0), (x1, y1) = LOWER_CREST
    lower = x0 + (x1 - x0) * min(1.0, max(0.0, (y - y0) / (y1 - y0)))
    f = smoothstep(-1.25, -0.55, y)
    return lower + (UPPER_CREST - lower) * f


def crest_distance(x, y):
    """How far (x, y) of the left case lies from its plates' crests."""
    upper = abs(x - UPPER_CREST) if y > UPPER_END[1] else math.hypot(x - UPPER_CREST, y - UPPER_END[1])
    (x0, y0), (x1, y1) = LOWER_CREST
    dx, dy = x1 - x0, y1 - y0
    t = max(0.0, min(1.0, ((x - x0) * dx + (y - y0) * dy) / (dx * dx + dy * dy)))
    lower = math.hypot(x - (x0 + dx * t), y - (y0 + dy * t))
    return min(upper, lower)


def case(m, side):
    """A wing case: the left one (side -1) or its mirror image (side 1), each painted by its own light (the sun
    shades them as the sprite does)."""
    s = -side  # the left case's x is s * x
    poly = ccw(mk.chaikin([(s * x, y) for x, y in CASE], 2))
    region = Region([poly])

    def top(x, y, d):
        return case_top(s * x, y, d)

    def shade(x, y, d):
        crest = CREST_LIGHT * max(0.0, 1.0 - crest_distance(s * x, y) / CREST_WIDTH) * min(1.0, d / EDGE)
        return light_of(top, region, x, y) + crest

    def paint(x, y, d):
        if streak_field(s * x, y) < 0.0:
            t, _ = streak_t(s * x, y)
            return next(index for limit, index in STREAK_REDS if t < limit)
        return steel_key(shade(x, y, d))

    borders = [(lambda x, y, d: streak_field(s * x, y), 0.0),
               (lambda x, y, d: streak_t(s * x, y)[0] - STREAK_REDS[0][0] if streak_field(s * x, y) < 0.3 else 1.0,
                0.0)]
    borders += [(lambda x, y, d, b=b: shade(x, y, d) - b, 0.0) for b in STEEL[0]]
    keys = dict(m)
    keys["side"] = m[STEEL[1][0]]
    left_rows = grid_rows(mk.chaikin(CASE, 2), ROW_STEP, crest_x, *CASE_SAMPLES)
    rows = left_rows if side < 0 else [[(-x, y) for x, y in reversed(row)] for row in left_rows]
    return grid_relief("case_" + ("l" if side < 0 else "r"), rows, top, keys, paint, borders, "side")


# --- The tail -----------------------------------------------------------------------------------------------------

def tail_at(y):
    pts = list(reversed(TAIL))
    return interp([(p[0], p[1]) for p in pts], y), interp([(p[0], p[2]) for p in pts], y)


def tail_plan():
    top, tip = TAIL[0][0], TAIL[-1][0]
    left = [(-tail_at(y)[0], y) for y in [top + (tip - top) * i / 48 for i in range(49)]]
    right = [(-x, y) for x, y in reversed(left)]
    return ccw(left + right)


CHEVRON_REGION = Region([CHEVRON, CHEVRON_NOTCH])


def chevron_field(x, y):
    """Negative inside the chevron (the triangle less its notch), the distance to its outline."""
    d = float(CHEVRON_REGION.distance([(x, y)])[0])
    return -d if CHEVRON_REGION.inside([(x, y)])[0] else d


def hot(x, y):
    return math.hypot(x - CHEVRON_HOT[0], y - CHEVRON_HOT[1])


def tail_top(x, y, d):
    w, z = tail_at(y)
    q = min(1.0, abs(x) / max(0.05, w))
    top = z * (1.0 - (1.0 - FULLNESS) * q ** 2.2)
    c = chevron_field(x, y)
    if c < 0.3:
        top += INLAY * smoothstep(0.3, -0.1, c)
    return max(0.25, top * round_edge(d, TAIL_EDGE))


def tail(m):
    poly = tail_plan()
    region = Region([poly])

    def shade(x, y, d):
        spine = SPINE_LIGHT * max(0.0, 1.0 - abs(x) / 1.1) * smoothstep(GROOVE_Y[1], GROOVE_Y[0], y)
        return light_of(tail_top, region, x, y) - GROOVE_SHADE * smoothstep(GROOVE_Y[0], GROOVE_Y[1], y) + spine

    def paint(x, y, d):
        if chevron_field(x, y) < 0.0:
            r = hot(x, y)
            return next(index for limit, index, _ in CHEVRON_REDS if r < limit)
        return steel_key(shade(x, y, d))

    borders = [(lambda x, y, d: chevron_field(x, y), 0.0)]
    borders += [(lambda x, y, d, lim=lim: hot(x, y) - lim if chevron_field(x, y) < 0.3 else 9.0, 0.0)
                for lim, _, _ in CHEVRON_REDS[:-1]]
    borders += [(lambda x, y, d, b=b: shade(x, y, d) - b, 0.0) for b in STEEL[0]]
    keys = dict(m)
    keys["side"] = m[STEEL[1][0]]
    rows = grid_rows(poly, ROW_STEP, lambda y: 0.0, *TAIL_SAMPLES)
    return grid_relief("tail", rows, tail_top, keys, paint, borders, "side")


def floor(m):
    plan, top = FLOOR
    poly = ccw(mk.chaikin(plan, 2))
    return relief("floor", [poly], lambda x, y, d: top * round_edge(d, 0.6), {"top": m["floor"], "side": m["floor"]},
                  side="side", bottom=0.0, spacing=1.2, smooth_angle=60.0)


def drop_undersides(objects):
    """Removes the flat undersides on the ground (never seen)."""
    for obj in objects:
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        under = [f for f in bm.faces if f.normal.z < -0.99 and max(v.co.z for v in f.verts) < 0.01]
        bmesh.ops.delete(bm, geom=under, context="FACES")
        bm.to_mesh(obj.data)
        bm.free()


def pin(m):
    e = 0.001
    return k.mesh_object("pin", [(0.0, 0.0, PIN_Z), (e, 0.0, PIN_Z), (0.0, e, PIN_Z)], [(0, 1, 2)], m["floor"])


def build():
    k.reset()
    options = k.args()
    out = mk.outdir(options)
    m = materials()
    case(m, -1)
    case(m, 1)
    tail(m)
    floor(m)
    drop_undersides(mk.meshes())
    pin(m)
    parts = triangulate(mk.meshes())
    bpy.context.view_layer.update()
    if "check" in options:
        mk.compare("botany_beetle (0 229)", mk.coverage(parts, 24, 28),
                   k.sprite_mask(os.path.join(options["check"], "enemy_0.png"), 229))
    bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
    mk.report("botany_beetle", parts, os.path.join(out, "botany_beetle.glb"))
    if "preview" in options:
        mk.preview(options["preview"] + "botany_beetle", parts)


if __name__ == "__main__":
    build()
