"""The glossy blocks of WINDY, SOH JIN and ASTEROID1 (sheet M, 2x2: 24 x 28 pixels, not animated;
models.cfg: yaw=0), polished (2026-10-18). One script, as they share one body and stand in the same
walls and grids:

- block_red (M 1): a red candy block (the sprite's ramp 4), a low ridge round a panel on its top.
- block_x (M 53): a purple-grey block (ramp 5) with a red brush-stroke X raised on its top (ramp 7): a
  falling stroke that starts with a little hook at the upper left and ends in a flick at the lower
  right, and a rising one, thin at its upper right end, that swells as it comes down and curls round
  into a hook at the lower left, its tail thinning out to the right.
- block_dollar (M 15): a green block (ramp 2) with a raised golden $ (ramp 7): an S of calligraphic
  strokes, thin at its ends and swelling in its curves, and a thinner bar laid over it.
- block_gem (M 17): an orange-bronze block (ramp 15) with a faceted blue gem (ramp 9) in a raised gold
  bezel shaped like a diamond, a dark red seat between them.
- block_chevron (M 153): a red block (ramp 4) with three chevrons embossed on its top, one above the
  other, pointing up the screen.
- block_question (M 55): a blue block (ramp 3) with a question mark and its dot embossed on its top.

As the 4x upscales draw them: soft, glossy blocks, rounded in plan, their top edge rolled over and
their top bulging a little, lit from the top left.

The body is blocks.py's (wave3_ah.py's broken blocks stand in the same walls, so its footprint,
height and dome stay): a superellipse of power 5 in plan, half sizes 11 x 12.6 (the sprites' dark
outlines are the gaps between neighbours), straight walls up to 5.4, the top edge rolled over from
there to 3.6 pixels in from the walls (as blocks.py's), where it meets the dome at the dome's own
slope (no crease), 9 high to the top's edge (9.3 in the middle of the sides, a little less towards
the corners, as a cushion's) and the top bulging 1.2 more in the middle (10.2). The walls' foot is
in the sprite's dark outline colour.

The sprites draw the blocks from the front and above: the top in rows 1-18, the front below it. The
emblems are drawn as the sprites show them, moved down the screen by EMBLEM_SHIFT (2.5 pixels) onto
the model's top, a little behind its middle, where the game's slanted camera (20 degrees) shows them
on the block as the sprites do; seen straight from above they sit lower than in the sprites. They
follow the domed top: raised strokes edged by a dark line for the X and the $ (the sprites' dark
pixels round them), soft embossing in the block's own colours for the chevrons and the question
mark, a faceted gem in a bezel.

Origin at the sprite's centre (pixel 12, 14); +Y up the sprite, +Z up from the ground (z = 0).

Replaces blocks.py (block_red, block_dollar, block_gem), later_episodes.py's block_x and
block_chevron and wave3_ah.py's block_question.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the
silhouette of each against its sprite in <dir>/enemy_M.png), --preview <prefix>, --only <name,...>.
"""
import math
import os
import sys

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
import tyrkit as k  # noqa: E402

# --- The body -------------------------------------------------------------------------------------

HALF_W, HALF_D, HEIGHT, DOME = 11.0, 12.6, 9.0, 1.2   # as blocks.py's and wave3_ah.py's blocks
TOP = HEIGHT + DOME
POWER = 5.0                  # the plan: |x / HALF_W|^5 + |y / HALF_D|^5 = 1
SEGMENTS = 72                # points round the plan
ROLL_WIDTH = 3.6             # the roll over the top edge: how far in from the walls it reaches
WALL_TOP = 5.4               # where the straight walls end and the roll begins
RIM_Z = 9.3                  # the dome's height where the roll meets it in the middle of the sides
DOME_POWER = 2.6             # the dome's contours: rounded rectangles, rounder than the plan
ROLL_STEPS, DOME_STEPS = 8, 6
DARK_Z = 1.1                 # the walls' foot, up to this height, in the sprite's outline colour

EMBLEM_SHIFT = 2.5           # the emblems: moved this far down the screen from where the sprites draw them


def superellipse(a, b, p, n):
    """n points on |x/a|^p + |y/b|^p = 1, evenly spaced along it, counter-clockwise from (a, 0)
    (n a multiple of 4 keeps them symmetric), with their outward normals."""
    m = 4096
    dense = []
    for i in range(m + 1):
        t = 2 * math.pi * i / m
        c, s = math.cos(t), math.sin(t)
        dense.append(Vector((a * math.copysign(abs(c) ** (2 / p), c), b * math.copysign(abs(s) ** (2 / p), s))))
    lengths = [0.0]
    for p0, p1 in zip(dense, dense[1:]):
        lengths.append(lengths[-1] + (p1 - p0).length)
    total = lengths[-1]
    points, normals = [], []
    j = 0
    for i in range(n):
        target = total * i / n
        while lengths[j + 1] < target:
            j += 1
        f = (target - lengths[j]) / (lengths[j + 1] - lengths[j])
        q = dense[j].lerp(dense[j + 1], f)
        points.append(q)
        g = Vector((math.copysign(abs(q.x / a) ** (p - 1), q.x) / a, math.copysign(abs(q.y / b) ** (p - 1), q.y) / b))
        normals.append(g.normalized())
    return points, normals


DOME_A, DOME_B = HALF_W - ROLL_WIDTH, HALF_D - ROLL_WIDTH


def dome_metric(x, y):
    """0 in the middle of the top, 1 where the roll meets it in the middle of the sides (more at its
    corners); its gradient."""
    q = DOME_POWER
    ux, uy = abs(x) / DOME_A, abs(y) / DOME_B
    s = ux ** q + uy ** q
    if s < 1e-12:
        return 0.0, Vector((0.0, 0.0))
    g = s ** (2 / q)
    common = 2 * s ** (2 / q - 1)
    return g, Vector((common * ux ** (q - 1) * math.copysign(1, x) / DOME_A,
                      common * uy ** (q - 1) * math.copysign(1, y) / DOME_B))


def dome_z(x, y):
    """The top: a dome over rounded-rectangle contours, TOP in the middle, RIM_Z at the middle of
    the roll's inner edge on each side, a little lower towards its corners (as a cushion's)."""
    return TOP - (TOP - RIM_Z) * dome_metric(x, y)[0]


def body_rings():
    """The body's rings from the ground up: (points (x, y, z)), the last one the dome's smallest."""
    outer, normals = superellipse(HALF_W, HALF_D, POWER, SEGMENTS)
    rings = []

    def wall(s, z):
        return [Vector((p.x - n.x * s, p.y - n.y * s, z)) for p, n in zip(outer, normals)]

    # The straight wall, its foot dark.
    rings += [wall(0.0, 0.0), wall(0.0, DARK_Z), wall(0.0, WALL_TOP)]
    # The roll over the top edge, an elliptic arc in each segment from the vertical wall to where it
    # meets the dome at the dome's own slope (so that they meet without a crease).
    arcs = []
    for p, n in zip(outer, normals):
        rim = p - n * ROLL_WIDTH
        g, grad = dome_metric(rim.x, rim.y)
        rise = TOP - (TOP - RIM_Z) * g - WALL_TOP        # the arc's height
        slope = (TOP - RIM_Z) * grad.dot(n)              # the dome's rise inwards at the rim
        c = slope * ROLL_WIDTH / (rise - slope * ROLL_WIDTH)
        end = math.acos(max(0.0, min(0.95, c)))
        arcs.append((end, ROLL_WIDTH / (1 - math.cos(end)), rise / math.sin(end)))
    for i in range(1, ROLL_STEPS + 1):
        ring = []
        for p, n, (end, rh, rv) in zip(outer, normals, arcs):
            a = end * i / ROLL_STEPS
            s = rh * (1 - math.cos(a))
            ring.append(Vector((p.x - n.x * s, p.y - n.y * s, WALL_TOP + rv * math.sin(a))))
        rings.append(ring)
    # The dome: the roll's inner edge drawn in towards the middle, rounder as it goes (an ellipse
    # at the middle); the heights are the dome's.
    rim = rings[-1]
    for j in range(1, DOME_STEPS + 1):
        f = 1 - (j / (DOME_STEPS + 1)) ** 0.9
        ring = []
        for q in rim:
            theta = math.atan2(q.y, q.x)
            r_ellipse = 1 / math.sqrt((math.cos(theta) / DOME_A) ** 2 + (math.sin(theta) / DOME_B) ** 2)
            r = (f * q.to_2d().length + (1 - f) * r_ellipse) * f
            x, y = r * math.cos(theta), r * math.sin(theta)
            ring.append(Vector((x, y, dome_z(x, y))))
        rings.append(ring)
    return rings


def body(name, shell, dark):
    """The block: one closed mesh, the walls' foot in `dark`."""
    rings = body_rings()
    n = SEGMENTS
    vertices = [tuple(p) for ring in rings for p in ring]
    faces, kinds = [], []
    for i in range(len(rings) - 1):
        dark_band = (rings[i][0].z + rings[i + 1][0].z) / 2 < DARK_Z
        for j in range(n):
            a, b = i * n + j, i * n + (j + 1) % n
            faces.append((a, b, b + n, a + n))
            kinds.append(1 if dark_band else 0)
    faces.append(tuple(reversed(range(n))))  # the bottom
    kinds.append(1)
    vertices.append((0.0, 0.0, TOP))
    top = (len(rings) - 1) * n
    for j in range(n):
        faces.append((top + j, top + (j + 1) % n, len(vertices) - 1))
        kinds.append(0)
    obj = k.mesh_object(name, vertices, faces)
    obj.data.materials.append(shell)
    obj.data.materials.append(dark)
    for poly, kind in zip(obj.data.polygons, kinds):
        poly.material_index = kind
    k.recalc_normals(obj)
    return k.smooth(obj, 50)


class Top:
    """The heights of the body's top (where the emblems lie), or of other parts, by casting rays
    down onto them."""

    def __init__(self, *objs):
        vertices, polygons = [], []
        for obj in objs:
            base = len(vertices)
            vertices += [obj.matrix_world @ v.co for v in obj.data.vertices]
            polygons += [[base + i for i in p.vertices] for p in obj.data.polygons]
        self.tree = BVHTree.FromPolygons(vertices, polygons)

    def z(self, x, y, default=0.0):
        hit = self.tree.ray_cast(Vector((x, y, 50.0)), Vector((0.0, 0.0, -1.0)))
        return hit[0].z if hit[0] is not None else default


# --- Raised strokes -------------------------------------------------------------------------------

def crisp(v):
    """A raised stroke's cross-section (v -1..1 across it): a rounded top, its sides steep at the foot."""
    return (1 - min(1.0, abs(v)) ** 2.6) ** (1 / 2.6)


def soft(v):
    """Embossing: a bump whose flanks run out gently into the top."""
    return math.cos(math.pi * min(1.0, abs(v)) / 2) ** 2


def bead(v):
    """A round bead lying on the top, its flanks drawn out a little at the foot."""
    return (1 - min(1.0, abs(v)) ** 2) ** 0.7


def spline(points, step):
    """A smooth path through points (x, y) (centripetal Catmull-Rom), resampled every `step` along it."""
    pts = [Vector(p) for p in points]
    pts = [pts[0] * 2 - pts[1]] + pts + [pts[-1] * 2 - pts[-2]]
    dense = []
    for i in range(1, len(pts) - 2):
        p0, p1, p2, p3 = pts[i - 1], pts[i], pts[i + 1], pts[i + 2]
        t0 = 0.0
        t1 = t0 + max((p1 - p0).length, 1e-4) ** 0.5
        t2 = t1 + max((p2 - p1).length, 1e-4) ** 0.5
        t3 = t2 + max((p3 - p2).length, 1e-4) ** 0.5
        for s in range(24):
            t = t1 + (t2 - t1) * s / 24
            a1 = p0 * ((t1 - t) / (t1 - t0)) + p1 * ((t - t0) / (t1 - t0))
            a2 = p1 * ((t2 - t) / (t2 - t1)) + p2 * ((t - t1) / (t2 - t1))
            a3 = p2 * ((t3 - t) / (t3 - t2)) + p3 * ((t - t2) / (t3 - t2))
            b1 = a1 * ((t2 - t) / (t2 - t0)) + a2 * ((t - t0) / (t2 - t0))
            b2 = a2 * ((t3 - t) / (t3 - t1)) + a3 * ((t - t1) / (t3 - t1))
            dense.append(b1 * ((t2 - t) / (t2 - t1)) + b2 * ((t - t1) / (t2 - t1)))
    dense.append(pts[-2])
    return resample(dense, step)


def resample(dense, step):
    """The polyline `dense` resampled to points evenly spaced, about `step` apart."""
    lengths = [0.0]
    for p0, p1 in zip(dense, dense[1:]):
        lengths.append(lengths[-1] + (p1 - p0).length)
    total = lengths[-1]
    count = max(2, int(round(total / step)))
    out, j = [], 0
    for i in range(count + 1):
        target = total * i / count
        while j < len(dense) - 2 and lengths[j + 1] < target:
            j += 1
        span = lengths[j + 1] - lengths[j]
        out.append(dense[j].lerp(dense[j + 1], (target - lengths[j]) / span if span > 0 else 0.0))
    return out


def ribbon(name, path, mat, top, half_width, height, shape=crisp, smooth=True, step=0.3, across=9, sink=0.12,
           round_start=False, round_end=False, lift=None, rim=None):
    """A stroke raised on the top along `path` (points (x, y)): smoothed through them, or straight
    between them with mitred corners (smooth=False). At a fraction t of its length it is
    2 * half_width(t) wide and height(t) high, its cross-section shape(v); its foot is sunk `sink`
    into the top. Round ends close it with a half dome, others with a point. lift(point, direction)
    raises each section (a stroke laid over another). rim (width, height, material): a narrow dark
    band round its foot, the stroke standing on it (the dark edge the sprites draw round emblems)."""
    if smooth:
        centre = spline(path, step)
        sections = []
        for i, p in enumerate(centre):
            d = (centre[min(i + 1, len(centre) - 1)] - centre[max(i - 1, 0)]).normalized()
            sections.append((p, Vector((-d.y, d.x)), 1.0, d))
    else:
        sections = []
        corners = [Vector(p) for p in path]
        for i in range(len(corners) - 1):
            p0, p1 = corners[i], corners[i + 1]
            d = (p1 - p0).normalized()
            nrm = Vector((-d.y, d.x))
            length = (p1 - p0).length
            # Room for the mitres at the corners: no sections within a half-width of them.
            skip0 = half_width(0.5) * 1.05 if i > 0 else 0.0
            skip1 = half_width(0.5) * 1.05 if i < len(corners) - 2 else 0.0
            count = max(1, int(round((length - skip0 - skip1) / step)))
            if i > 0:  # the mitre at the corner p0
                dp = (p0 - corners[i - 1]).normalized()
                bis = (Vector((-dp.y, dp.x)) + nrm).normalized()
                sections.append((p0, bis, 1 / max(0.3, bis.dot(nrm)), (dp + d).normalized()))
            for s in range(count + 1):
                along = skip0 + (length - skip0 - skip1) * s / count
                sections.append((p0 + d * along, nrm, 1.0, d))
    lengths = [0.0]
    for (p0, *_), (p1, *_) in zip(sections, sections[1:]):
        lengths.append(lengths[-1] + (p1 - p0).length)
    total = lengths[-1]

    # Across: closer together at the edges for steep-sided strokes, even for embossing.
    if shape is soft:
        vs = [-1 + 2 * i / (across - 1) for i in range(across)]
    else:
        vs = [math.sin(math.pi / 2 * (-1 + 2 * i / (across - 1))) for i in range(across)]
    rings = []
    foot = rim[1] if rim else -sink   # the stroke's foot: on its rim, or sunk into the top

    def section(p, nrm, mitre, w, h, d):
        up = lift(p, d) if lift is not None else 0.0
        pts = []
        for v in vs:
            q = p + nrm * (v * w * mitre)
            pts.append(Vector((q.x, q.y, top.z(q.x, q.y) + up + foot + (h - foot) * shape(v))))
        if rim:
            edges = []
            for side in (-1, 1):
                q = p + nrm * (side * (w * mitre + rim[0]))
                edges.append(Vector((q.x, q.y, top.z(q.x, q.y) + up - 0.06)))
            pts = [edges[0]] + pts + [edges[1]]
        return pts

    for (p, nrm, mitre, d), s in zip(sections, lengths):
        t = s / total if total > 0 else 0.0
        rings.append(section(p, nrm, mitre, half_width(t), height(t), d))

    def cap(end, sign):
        """Rings beyond an end, closing it with a half dome; returns them (outwards) and the tip."""
        p, nrm, mitre, d = sections[end]
        t = 1.0 if end else 0.0
        w, h = half_width(t), height(t)
        extra = []
        for j in range(1, 4):
            phi = math.pi / 2 * j / 4
            centre = p + d * (sign * w * math.sin(phi))
            extra.append(section(centre, nrm, mitre, w * math.cos(phi), h * math.cos(phi), d))
        tip = p + d * (sign * w)
        return extra, Vector((tip.x, tip.y, top.z(tip.x, tip.y) + max(0.0, h * 0.15) - sink * 0.5))

    start_tip = end_tip = None
    if round_start:
        extra, start_tip = cap(0, -1)
        rings = list(reversed(extra)) + rings
    if round_end:
        extra, end_tip = cap(len(sections) - 1, 1)
        rings = rings + extra
    # One open sheet over the top (its edges sunk into it), facing up; the ends closed by fans.
    m = len(rings[0])
    vertices = [v for r in rings for v in r]
    faces, kinds = [], []
    for i in range(len(rings) - 1):
        for j in range(m - 1):
            a, b = i * m + j, i * m + j + 1
            faces.append((a, a + m, b + m, b))
            kinds.append(j)
    vertices.append(start_tip if start_tip is not None else sum(rings[0], Vector()) / m)
    c = len(vertices) - 1
    faces += [(j, j + 1, c) for j in range(m - 1)]
    kinds += list(range(m - 1))
    vertices.append(end_tip if end_tip is not None else sum(rings[-1], Vector()) / m)
    c = len(vertices) - 1
    base = (len(rings) - 1) * m
    faces += [(base + j + 1, base + j, c) for j in range(m - 1)]
    kinds += list(range(m - 1))
    obj = k.mesh_object(name, vertices, faces, mat)
    if rim:  # the outermost strip either side
        obj.data.materials.append(rim[2])
        for poly, j in zip(obj.data.polygons, kinds):
            poly.material_index = 1 if j in (0, m - 2) else 0
    return k.smooth(obj, 70)


def bump(name, centre, radii, height, mat, top, rings=6, segments=20, sink=0.1):
    """A round boss embossed on the top (an elliptic dome whose edge runs out into the top)."""
    cx, cy = centre
    vertices = []
    for i in range(rings, 0, -1):
        f = i / rings
        for j in range(segments):
            a = 2 * math.pi * j / segments
            x, y = cx + radii[0] * f * math.cos(a), cy + radii[1] * f * math.sin(a)
            vertices.append((x, y, top.z(x, y) + (height + sink) * (1 - f * f) ** 0.6 - sink))
    vertices.append((cx, cy, top.z(cx, cy) + height))
    faces = []
    for i in range(rings - 1):
        for j in range(segments):
            a, b = i * segments + j, i * segments + (j + 1) % segments
            faces.append((a, b, b + segments, a + segments))
    last = (rings - 1) * segments
    faces += [(last + j, last + (j + 1) % segments, len(vertices) - 1) for j in range(segments)]
    return k.smooth(k.mesh_object(name, vertices, faces, mat), 70)


def at(col, row):
    """A point the sprite (its 4x upscale) draws at column col and row row (pixel edges at whole
    numbers), on the model's top: moved down the screen by EMBLEM_SHIFT."""
    return (col - 12.0, 14.0 - row - EMBLEM_SHIFT)


def ramp(*knots):
    """A smooth function of t (0-1) through the knots (t, value): monotone between them (a
    piecewise cubic that does not overshoot), so that strokes swell and taper without kinks."""
    ts = [t for t, _ in knots]
    vs = [v for _, v in knots]
    n = len(knots)
    if n == 1:
        return lambda t: vs[0]
    d = [(vs[i + 1] - vs[i]) / (ts[i + 1] - ts[i]) for i in range(n - 1)]
    m = [d[0]] + [0.0 if d[i - 1] * d[i] <= 0 else 2 / (1 / d[i - 1] + 1 / d[i]) for i in range(1, n - 1)] + [d[-1]]

    def f(t):
        if t <= ts[0]:
            return vs[0]
        if t >= ts[-1]:
            return vs[-1]
        i = max(j for j in range(n - 1) if ts[j] <= t)
        h = ts[i + 1] - ts[i]
        u = (t - ts[i]) / h
        h00, h10 = 2 * u ** 3 - 3 * u ** 2 + 1, u ** 3 - 2 * u ** 2 + u
        h01, h11 = -2 * u ** 3 + 3 * u ** 2, u ** 3 - u ** 2
        return h00 * vs[i] + h10 * h * m[i] + h01 * vs[i + 1] + h11 * h * m[i + 1]
    return f


# --- The emblems ----------------------------------------------------------------------------------

def emblem_x(top, mats):
    """The red brush-stroke X (the upscale's columns 6-19.5, rows 4-17)."""
    red = mats["red"]
    rim = (0.3, 0.1, mats["edge"])   # the dark edge round the strokes
    h = 0.56   # the falling stroke; the rising one stands a little higher, over it where they cross
    # The falling stroke: a short hook at its upper left end, the stroke itself, a flick at its end.
    ribbon("x_hook", [at(6.05, 6.05), at(6.6, 5.45), at(7.35, 5.1), at(8.0, 5.25)], red, top,
           ramp((0, 0.34), (0.5, 0.56), (1, 0.64)), ramp((0, 0.3), (0.4, h * 0.92), (1, h * 0.75)),
           round_start=True, rim=rim)
    ribbon("x_fall", [at(7.55, 5.15), at(8.5, 5.62), at(9.5, 6.32), at(10.5, 7.12), at(11.5, 7.95), at(12.5, 8.8),
                      at(13.5, 9.7), at(14.5, 10.6), at(15.5, 11.5), at(16.5, 12.38), at(17.35, 13.05)], red, top,
           ramp((0, 0.7), (0.5, 0.77), (1, 0.72)), lambda t: h, round_start=True, round_end=True, rim=rim)
    ribbon("x_flick", [at(16.7, 12.52), at(17.4, 13.08), at(18.0, 12.95), at(18.6, 12.55), at(19.25, 11.95)], red,
           top, ramp((0, 0.6), (0.4, 0.58), (1, 0.14)),
           ramp((0, h * 0.6), (0.3, h * 0.72), (0.5, h * 0.9), (1, h * 0.35)), round_end=True, rim=rim)
    # The rising stroke: thin at its upper right end, swelling as it comes down to the lower left,
    # where it curls round into a hook and thins out to the right.
    ribbon("x_rise", [at(19.15, 4.1), at(18.0, 5.0), at(17.0, 5.8), at(16.0, 6.6), at(15.0, 7.35), at(14.0, 8.1),
                      at(13.0, 8.9), at(12.0, 9.75), at(11.0, 10.45), at(10.0, 11.2), at(9.0, 12.0), at(8.15, 12.95),
                      at(7.68, 14.0), at(7.78, 14.95), at(8.4, 15.65), at(9.4, 16.2), at(10.5, 16.6), at(11.65, 16.9)],
           red, top, ramp((0, 0.08), (0.08, 0.48), (0.3, 0.68), (0.5, 0.84), (0.62, 1.06), (0.72, 1.22), (0.8, 1.1),
                          (0.88, 0.84), (0.95, 0.48), (1, 0.08)),
           ramp((0, 0.1), (0.1, h + 0.1), (0.9, h + 0.1), (1, 0.12)), step=0.26, round_start=True, round_end=True,
           rim=rim)


def emblem_dollar(top, mats):
    """The golden $ (the upscale's columns 7-16, rows 3-19)."""
    gold = mats["gold"]
    rim = (0.28, 0.1, mats["edge"])   # the dark edge round the strokes
    s = ribbon("s", [at(15.3, 5.0), at(14.4, 5.35), at(13.0, 5.5), at(11.6, 5.52), at(10.2, 5.65), at(9.0, 6.05),
                     at(8.0, 6.75), at(7.5, 7.7), at(7.55, 8.7), at(8.1, 9.6), at(9.1, 10.2), at(10.5, 10.58),
                     at(12.0, 10.82), at(13.3, 11.17), at(14.4, 11.8), at(15.1, 12.8), at(15.32, 13.9), at(15.0, 14.9),
                     at(14.1, 15.65), at(12.8, 16.05), at(11.2, 16.15), at(9.6, 16.2), at(8.2, 16.3), at(7.05, 16.42)],
           gold, top, ramp((0, 0.32), (0.05, 0.5), (0.12, 0.6), (0.22, 0.78), (0.3, 0.97), (0.38, 0.93), (0.5, 0.8),
                           (0.62, 0.88), (0.7, 0.95), (0.78, 0.78), (0.88, 0.63), (0.96, 0.44), (1, 0.3)),
           ramp((0, 0.32), (0.06, 0.58), (0.94, 0.58), (1, 0.3)), shape=bead, step=0.26, round_start=True,
           round_end=True, rim=rim)
    # The bar, laid over the S: a little teardrop at its top, a point at its foot.
    over = Top(s)

    def lift(p, d):
        best = 0.0
        for along, weight in ((0.0, 1.0), (0.3, 0.95), (-0.3, 0.95), (0.6, 0.8), (-0.6, 0.8), (0.9, 0.5), (-0.9, 0.5),
                              (1.2, 0.2), (-1.2, 0.2)):
            q = p + d * along
            best = max(best, weight * max(0.0, over.z(q.x, q.y, -9.0) - top.z(q.x, q.y) - 0.15))
        return best

    ribbon("bar", [at(11.42, 3.15), at(11.42, 6.0), at(11.4, 11.0), at(11.4, 16.0), at(11.38, 18.9)], gold, top,
           ramp((0, 0.46), (0.08, 0.48), (0.18, 0.42), (0.85, 0.42), (0.93, 0.32), (1, 0.1)),
           ramp((0, 0.6), (0.9, 0.6), (1, 0.16)), shape=bead, round_start=True, round_end=True, lift=lift, rim=rim)


def emblem_question(top, mats):
    """The embossed question mark (the upscale's columns 9-15, rows 5-16.6)."""
    mark = mats["mark"]
    ribbon("hook", [at(9.2, 8.1), at(9.0, 7.1), at(9.4, 6.1), at(10.3, 5.4), at(11.5, 5.05), at(12.7, 5.1),
                    at(13.8, 5.6), at(14.6, 6.4), at(14.95, 7.4), at(14.75, 8.5), at(14.15, 9.5), at(13.4, 10.4),
                    at(12.6, 11.25), at(12.0, 12.05), at(11.72, 12.9)], mark, top,
           ramp((0, 0.76), (0.7, 0.73), (1, 0.68)), lambda t: 0.66, shape=bead, sink=0.08,
           round_start=True, round_end=True)
    bump("dot", at(11.65, 15.7), (1.2, 1.05), 0.68, mark, top)


def emblem_chevrons(top, mats):
    """Three chevrons, one above the other (the upscale's apexes in column 12, rows 3, 7 and 11.5;
    their arms down to columns 7.5 and 16.5, 4.4 rows lower)."""
    ridge = mats["ridge"]
    for i, apex in enumerate((3.0, 7.05, 11.4)):
        ribbon(f"chevron{i}", [at(7.5, apex + 4.4), at(12.0, apex), at(16.5, apex + 4.4)], ridge, top,
               ramp((0, 0.55), (0.14, 0.8), (0.86, 0.8), (1, 0.55)),
               ramp((0, -0.06), (0.14, 0.46), (0.86, 0.46), (1, -0.06)), shape=soft, smooth=False, across=11,
               sink=0.05)


def emblem_panel(top, mats):
    """A low ridge in the block's own colour round a panel on its top (columns 5-19, rows 4.5-14.5), its corners
    mitred: the plain red blocks read as smooth pillows in the game's light (2026-10-30), a little more than the
    sprite, which draws them plain."""
    ridge = mats["ridge"]
    path = [at(12.0, 4.5), at(19.0, 4.5), at(19.0, 14.5), at(5.0, 14.5), at(5.0, 4.5), at(12.0, 4.5)]
    ribbon("panel", path, ridge, top, lambda t: 0.5, lambda t: 0.42, shape=soft, smooth=False, across=11, sink=0.05,
           round_start=True, round_end=True)


def bezel_ring(name, centre, outline, profile, mats, top):
    """A ring round the closed outline [(x, y) relative to centre, counter-clockwise]: profile
    [(offset out from the outline, height above the top, material key)] from its inside to its
    outside."""
    n = len(outline)
    pts = [Vector(p) for p in outline]
    normals = []
    for i in range(n):
        d = (pts[(i + 1) % n] - pts[i - 1]).normalized()
        normals.append(Vector((d.y, -d.x)))
    vertices, faces, kinds = [], [], []
    for off, z, _ in profile:
        for p, nrm in zip(pts, normals):
            q = Vector(centre) + p + nrm * off
            vertices.append((q.x, q.y, top.z(q.x, q.y) + z))
    for r in range(len(profile) - 1):
        for i in range(n):
            a, b = r * n + i, r * n + (i + 1) % n
            faces.append((a, a + n, b + n, b))
            kinds.append(profile[r][2])
    keys = []
    for kind in kinds:
        if kind not in keys:
            keys.append(kind)
    obj = k.mesh_object(name, vertices, faces)
    for key in keys:
        obj.data.materials.append(mats[key])
    for poly, kind in zip(obj.data.polygons, kinds):
        poly.material_index = keys.index(kind)
    return k.smooth(obj, 40)


def diamond(side, q, count, offset=0.0):
    """A square turned 45 degrees (corners up, down, left and right), its corners rounded (a
    superellipse of power q in the turned frame), `side` from its middle to the middle of its sides:
    count points counter-clockwise, starting `offset` (a fraction of a step) past the middle of its
    upper right side."""
    out = []
    r = side / math.sqrt(2)
    for i in range(count):
        a = 2 * math.pi * (i + offset) / count
        c, s = math.cos(a), math.sin(a)
        u = math.copysign(abs(c) ** (2 / q), c)
        v = math.copysign(abs(s) ** (2 / q), s)
        out.append((r * (u - v), r * (u + v)))
    return out


GEM_SIDE, GEM_POWER = 2.9, 4.2   # the gem's girdle: the upscale's blue, 7 pixels from corner to corner


def emblem_gem(top, mats):
    """The blue gem in its gold bezel (the upscale's gem: columns 8.6-15.6, rows 6.4-13.8, its
    bezel a pixel wider all round, a dark red seat between them)."""
    centre = at(12.1, 10.1)
    seat = diamond(GEM_SIDE + 0.06, GEM_POWER, 64)
    profile = [(-0.15, 0.3, "seat"), (0.0, 0.42, "seat"), (0.05, 0.72, "bezel"), (0.22, 0.92, "bezel"),
               (0.45, 0.98, "bezel"), (0.7, 0.9, "bezel"), (0.92, 0.65, "bezel"), (1.06, 0.32, "bezel"),
               (1.14, 0.0, "bezel"), (1.18, -0.12, "bezel")]
    bezel_ring("bezel", centre, seat, profile, mats, top)
    # The gem, cut in facets: from its girdle (a rounded diamond) sixteen upper girdle facets and
    # sixteen more up to a ring halfway in, kites and stars up to an octagonal table.
    cx, cy = centre
    cz = top.z(cx, cy)
    rings = [(diamond(GEM_SIDE, GEM_POWER, 16), 0.4), (diamond(GEM_SIDE * 0.8, GEM_POWER, 16, 0.5), 1.0),
             (diamond(GEM_SIDE * 0.42, GEM_POWER, 8), 1.4)]
    vertices = [(cx + x, cy + y, cz + z) for ring, z in rings for x, y in ring]
    vertices.append((cx, cy, cz + 0.1))
    a, b, c = 0, 16, 32
    faces, kinds = [], []
    for i in range(16):
        j = (i + 1) % 16
        faces += [(a + i, a + j, b + i), (a + j, b + j, b + i)]
        kinds += ["crown", "crown"]
    for i in range(8):
        j = (i + 1) % 8
        faces.append((b + (2 * i - 1) % 16, b + 2 * i, c + i))
        faces.append((c + i, b + 2 * i, b + 2 * i + 1, c + j))
        kinds += ["star", "star"]
    faces.append(tuple(c + i for i in range(8)))
    kinds.append("table")
    faces += [((i + 1) % 16, i, len(vertices) - 1) for i in range(16)]
    kinds += ["crown"] * 16
    keys = []
    for kind in kinds:
        if kind not in keys:
            keys.append(kind)
    obj = k.mesh_object("gem", vertices, faces)
    for key in keys:
        obj.data.materials.append(mats[key])
    for poly, kind in zip(obj.data.polygons, kinds):
        poly.material_index = keys.index(kind)
        poly.use_smooth = False
    k.recalc_normals(obj)
    return obj


# --- The models -----------------------------------------------------------------------------------

# The blocks: name -> (sprite, the body's palette index, its outline's, the emblem).
BLOCKS = {
    "block_red": (1, 0x47, 0x01, emblem_panel),
    "block_x": (53, 0x57, 0x50, emblem_x),
    "block_dollar": (15, 0x27, 0x20, emblem_dollar),
    "block_gem": (17, 0xf9, 0xf2, emblem_gem),
    "block_chevron": (153, 0x47, 0x01, emblem_chevrons),
    "block_question": (55, 0x39, 0x32, emblem_question),
}


def emblem_materials(name, shell):
    """The emblem's materials by the keys its builder uses (the chevrons are the body's own)."""
    if name == "block_x":
        return {"red": k.material("blockx_red", palette=0x77, metallic=0.1, roughness=0.22),
                "edge": k.material("blockx_edge", palette=0x53, metallic=0.05, roughness=0.6)}
    if name == "block_dollar":
        return {"gold": k.material("dollar_gold", palette=0x7d, metallic=0.35, roughness=0.26),
                "edge": k.material("dollar_edge", palette=0x24, metallic=0.05, roughness=0.6)}
    if name == "block_gem":
        # The gem lights up a little in its own blues, as the sprite's bright gem does.
        glow = k.level_palette()
        return {"bezel": k.material("gem_bezel", palette=0xfa, metallic=0.3, roughness=0.24),
                "seat": k.material("gem_seat", palette=0x47, metallic=0.2, roughness=0.45),
                "crown": k.material("gem_crown", palette=0x9a, metallic=0.1, roughness=0.08, emission=glow[0x9a],
                                    emission_strength=0.35),
                "star": k.material("gem_star", palette=0x9c, metallic=0.1, roughness=0.08, emission=glow[0x9c],
                                   emission_strength=0.45),
                "table": k.material("gem_table", palette=0x9e, metallic=0.1, roughness=0.06, emission=glow[0x9e],
                                    emission_strength=0.55)}
    if name in ("block_chevron", "block_red"):
        return {"ridge": shell}
    if name == "block_question":
        return {"mark": k.material("question_mark", palette=0x3a, metallic=0.05, roughness=0.24)}
    return {}


def model(name):
    """Builds the block `name` (its body and emblem) in the scene."""
    sprite, shade, outline, emblem = BLOCKS[name]
    # Glossy candy; the walls' foot matt and dark.
    shell = k.material(name + "_shell", palette=shade, metallic=0.05, roughness=0.3)
    dark = k.material(name + "_outline", palette=outline, metallic=0.0, roughness=0.85)
    block = body("block", shell, dark)
    if emblem is not None:
        emblem(Top(block), emblem_materials(name, shell))


def triangles():
    depsgraph = bpy.context.evaluated_depsgraph_get()
    total = 0
    for obj in bpy.context.scene.objects:
        if obj.type == "MESH":
            mesh = obj.evaluated_get(depsgraph).to_mesh()
            mesh.calc_loop_triangles()
            total += len(mesh.loop_triangles)
            obj.evaluated_get(depsgraph).to_mesh_clear()
    return total


def build():
    options = k.args()
    outdir = options.get("outdir", os.path.join(HERE, "..", "..", "..", "..", "assets", "models", "enemies"))
    only = options["only"].split(",") if "only" in options else list(BLOCKS)
    for name in only:
        k.reset()
        model(name)
        sprite = BLOCKS[name][0]
        materials = {m.name for o in bpy.context.scene.objects if o.type == "MESH" for m in o.data.materials}
        print("== %s (M %d): %d triangles, %d materials" % (name, sprite, triangles(), len(materials)))
        if "check" in options:
            k.check_silhouette(os.path.join(options["check"], "enemy_M.png"), sprite)
        bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
        path = os.path.join(outdir, name + ".glb")
        k.export(path)
        print("   %s: %.1f KB" % (name, os.path.getsize(path) / 1024))
        if "preview" in options:
            k.preview(options["preview"] + name)


if __name__ == "__main__":
    build()
