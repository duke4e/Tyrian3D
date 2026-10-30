"""The store's shields as 3D models (2026-10-30): models.cfg "shield <id> <model>" gives each shield (ids as in the
shop) a model, whose render (assets/models/icons/<model>.png, made by TYR3D_RENDER_ICONS) the store's cards, its
Upgrade Ship rows and the rogue run's cards show instead of the shop sheet's 2x2 item graphic. The shields were the
store's last items without models.

The item data (tyrian.hdt for episodes 1-3, the level files for 4 and 5) gives eleven shields nine pictures:

  picture  model               shields                                    the picture
  129      store_shield_129    1 Structural Integrity Field              a blue glass ball over a grey emitter
  131      store_shield_131    2 Advanced Integrity Field                the same with a bronze ball, wider feet
  153      store_shield_153    3 Gencore Low, 4 High Energy Shield       a grey heater shield, its top a bronze band,
                                                                          a spine down its middle
  155      store_shield_155    5 MicroCorp LXS Class A                   a narrow grey shield, a red core, four lamps
  157      store_shield_157    6 MicroCorp LXS Class B                   the wide shield with its spine, a red core each
                                                                          side, two lamps, red vents through the rim
  159      store_shield_159    7 MicroCorp LXS Class C                   the wide shield, one wide red core, four
                                                                          lamps, a nozzle under the core
  161      store_shield_161    9 MicroCorp HXS Class A                   a narrow shield, a green cell box on top, a
                                                                          green core, a round grey foot
  163      store_shield_163    10 MicroCorp HXS Class B                  the wide shield, a green arch over the spine,
                                                                          two green cells, a wide green core
  165      store_shield_165    11 MicroCorp HXS Class C                  as 163 with the arch split by the spine and a
                                                                          nozzle in the core
  (153/165) store_shield_solar 8 Gencore Solar Shield                    see below

The Gencore Solar Shield's picture is 165 (HXS Class C's) in episodes 1-3 and 153 (the Gencore heater shield) in 4
and 5; a shield has one model in every episode, so it gets its own: the Gencore heater shield (153's build) with green
solar cells in its two faces (165's green), not a copy of HXS Class C's.

The classes share builds: the wide shield (153, 157, 159, 163, 165 and the solar one: one outline, spine and frame),
its parts added by class; 155 and 161 are narrow ones; 129 and 131 one build with its ball and feet changed. Every
shield body is a solid over its outline (piece(): its front a height field, rounded at the edge, sampled on rings
along the outline), its front a low ridge down the middle; the MicroCorp ones and Gencore's in a raised border.

What the icons taught (each judged at the size the store's rows draw them, about 50 pixels at 1600 x 900):
- Seen as the icon sees it, a plain heater shield read as a spade: its spine, full width out of the top edge, was the
  handle, and its wide notch the blade's. The spine now narrows into a short point over the top edge, the notch
  between the points is a narrow slot, and the face has a raised border.
- The glass ball: see-through glass shadowed itself in speckles in the icon; glow_spot's lit patches had ragged edges.
  It is opaque, in bands by its slope (dark at the rim, light in the middle, as the picture shades it) with a glint.
- A rounded edge sampled only by a grid came out jagged; the rings along the outline fixed it.

Coordinates as in tyrkit (the store's other items, au_generators.py, are built the same way): 1 unit = 1 pixel of the
24 x 28 picture, +X right, +Y up the picture, +Z towards the viewer, the origin the picture's centre (column c is
x = c + 0.5 - 12, row r is y = 13.5 - r). The shields' backs are flat at z = 0, their fronts rise to about 4.5 (the
balls are deeper). The icon renderer shows them from below the picture's bottom edge and to its right, 55 degrees up,
turned 30 degrees (render_gpu.c rgpu_render_icons): faces towards -Y and the viewer show, faces towards +Y don't. The
pictures' black outline is the edge of the object (the models reach half way into it); their brown drop shadow isn't
part of it. Colours are fixed (the store's palette, which is the levels'), not palette materials: the icons are
rendered once.

Options after "--": --outdir <dir> (default assets/models/items), --check <dir> (the silhouette of each model against
its picture, <dir>/shop_<n>.png from TYR3D_EXPORT_PICTURES' icons/), --preview <prefix> (a top view framed like the
picture and the icon's view), --only <name,...>.
"""
import bisect
import math
import os
import sys

import bpy
import numpy as np
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polish_item_kit as kit  # noqa: E402
from polish_item_kit import k  # noqa: E402
import polish_powerups_specials as ps  # noqa: E402  (relief, band, catmull, triangulate)
sys.path.insert(0, os.path.join(HERE, "..", "store"))
import au_rear_kit as a  # noqa: E402  (glow_spot: the generators' lit patches on a sphere)
import polish_powerups_specials_rest as psr  # noqa: E402  (ball: an ellipsoid in bands by its slope)


# --- The picture's grid --------------------------------------------------------------------------------------------

def X(c):
    """The centre of column c."""
    return c + 0.5 - 12


def Y(r):
    """The centre of row r."""
    return 13.5 - r


def smoothstep(e0, e1, v):
    t = max(0.0, min(1.0, (v - e0) / (e1 - e0)))
    return t * t * (3 - 2 * t)


def rounded_rect(x0, x1, y0, y1, r, steps=4):
    """A rectangle with rounded corners (radius r), counter-clockwise."""
    r = min(r, (x1 - x0) / 2, (y1 - y0) / 2)
    out = []
    corners = [(x1 - r, y0 + r, -90), (x1 - r, y1 - r, 0), (x0 + r, y1 - r, 90), (x0 + r, y0 + r, 180)]
    for cx, cy, a0 in corners:
        for i in range(steps + 1):
            a = math.radians(a0 + 90 * i / steps)
            p = (cx + r * math.cos(a), cy + r * math.sin(a))
            if not out or math.hypot(p[0] - out[-1][0], p[1] - out[-1][1]) > 1e-3:
                out.append(p)
    if math.hypot(out[0][0] - out[-1][0], out[0][1] - out[-1][1]) < 1e-3:
        out.pop()
    return out


def mirrored(points, cx):
    """The right half of an outline from its left half (points from the top of the centre line down the left side
    to the bottom of the centre line, counter-clockwise): the whole outline, counter-clockwise."""
    right = [(2 * cx - x, y) for x, y in reversed(points)]
    return points + right[1:-1] if abs(points[-1][0] - cx) < 1e-6 and abs(points[0][0] - cx) < 1e-6 else points + right


def smooth_path(points, samples=4):
    return [(p.x, p.y) for p in ps.catmull([(x, y, 0.0) for x, y in points], samples)]


# --- Materials -----------------------------------------------------------------------------------------------------

def mat(name, rgb, metallic=0.5, roughness=0.35, emission=None, strength=1.0, alpha=None):
    return k.material("shield_" + name, rgb, metallic=metallic, roughness=roughness, emission=emission,
                      emission_strength=strength, alpha=alpha)


def materials():
    return {
        "steel": mat("steel", (150, 152, 150), 0.6, 0.3),
        "steel_light": mat("steel_light", (192, 194, 192), 0.6, 0.24),
        "steel_dark": mat("steel_dark", (66, 66, 68), 0.55, 0.4),
        "black": mat("black", (24, 24, 26), 0.4, 0.5),
        "bronze": mat("bronze", (204, 164, 116), 0.55, 0.3),
        "bronze_dark": mat("bronze_dark", (66, 42, 22), 0.5, 0.45),
        "gold": mat("gold", (250, 200, 60), 0.85, 0.22),
        "red": mat("red_core", (168, 10, 0), 0.0, 0.2, emission=(225, 22, 0), strength=0.75),
        "red_rib": mat("red_rib", (236, 104, 16), 0.0, 0.2, emission=(255, 108, 20), strength=1.3),
        "orange": mat("lamp_orange", (240, 112, 20), 0.0, 0.25, emission=(255, 112, 20), strength=2.0),
        "yellow": mat("lamp_yellow", (250, 196, 56), 0.0, 0.25, emission=(255, 204, 64), strength=2.4),
        "green": mat("green_core", (36, 104, 32), 0.0, 0.2, emission=(36, 160, 36), strength=0.7),
        "green_rib": mat("green_rib", (160, 206, 118), 0.0, 0.2, emission=(150, 236, 104), strength=1.1),
        "green_cell": mat("green_cell", (96, 176, 72), 0.0, 0.2, emission=(96, 236, 72), strength=1.3),
        "green_solar": mat("green_solar", (30, 86, 30), 0.3, 0.12, emission=(20, 110, 24), strength=0.45),
        "red_dot": mat("red_dot", (140, 0, 0), 0.0, 0.3, emission=(255, 24, 0), strength=1.6),
        "steel_mid": mat("steel_mid", (112, 114, 112), 0.6, 0.32),
        "glass": mat("glass_blue", (34, 76, 118), 0.15, 0.05, emission=(14, 44, 86), strength=0.35),
        "field": mat("field_blue", (44, 96, 152), 0.1, 0.06, emission=(30, 84, 170), strength=0.4),
        "field_hot": mat("field_hot", (84, 146, 206), 0.05, 0.06, emission=(70, 136, 226), strength=0.6),
        "glint": mat("glint", (226, 240, 252), 0.0, 0.05, emission=(200, 225, 255), strength=1.0),
    }


M = {}


# --- Shared parts --------------------------------------------------------------------------------------------------

EDGE_RINGS = (0.08, 0.22, 0.42, 0.7)


def piece(name, outline, height, m, bottom=0.0, step=0.5, rings=EDGE_RINGS, edge_step=0.3):
    """A solid over a plan: its top z = height(x, y, d), d the distance in from this outline, its walls straight
    down to z = bottom, its underside flat. As ps.relief, but the top's points also lie on rings at the distances
    `rings` in from the outline (the rounded edges and rims sampled evenly all round: a grid alone left them
    jagged), the grid only further in."""
    from mathutils.geometry import delaunay_2d_cdt
    import bmesh
    ring = ps.resample(outline, edge_step)
    nb = len(ring)
    points = [Vector(p) for p in ring]
    taken = []

    def far_from_taken(q, gap):
        return all((q[0] - t[0]) ** 2 + (q[1] - t[1]) ** 2 > gap * gap for t in taken)
    for d in rings:
        for i in range(nb):
            (ax, ay), (bx, by) = ring[i - 1], ring[(i + 1) % nb]
            tx, ty = bx - ax, by - ay
            length = math.hypot(tx, ty)
            if length < 1e-9:
                continue
            q = (ring[i][0] - ty / length * d, ring[i][1] + tx / length * d)
            if not ps.inside(q, outline):
                continue
            dist = ps.edge_distance(q, outline)
            if abs(dist - d) > 0.25 * d + 0.02 or not far_from_taken(q, edge_step * 0.55):
                continue
            taken.append(q)
            points.append(Vector(q))
    deepest = max(rings) if rings else 0.0
    xs, ys = [p[0] for p in ring], [p[1] for p in ring]
    row, y = 0, min(ys) + step * 0.5
    while y < max(ys):
        x = min(xs) + (step * 0.5 if row % 2 else 0.0)
        while x < max(xs):
            if ps.inside((x, y), outline) and ps.edge_distance((x, y), outline) > deepest + step * 0.45:
                points.append(Vector((x, y)))
            x += step
        y += step * 0.866
        row += 1
    edges = [(i, (i + 1) % nb) for i in range(nb)]
    verts2, _, faces, orig, _, _ = delaunay_2d_cdt(points, edges, [list(range(nb))], 1, 1e-6)
    bm = bmesh.new()
    top = [bm.verts.new((v.x, v.y, height(v.x, v.y, ps.edge_distance((v.x, v.y), outline)))) for v in verts2]
    boundary = [None] * nb
    for out_index, sources in enumerate(orig):
        for s in sources:
            if s < nb:
                boundary[s] = out_index
    for f in faces:
        bm.faces.new([top[i] for i in f])
    low = [bm.verts.new((top[boundary[i]].co.x, top[boundary[i]].co.y, bottom)) for i in range(nb)]
    for i in range(nb):
        j = (i + 1) % nb
        bm.faces.new((low[i], low[j], top[boundary[j]], top[boundary[i]]))
    bm.faces.new(list(reversed(low)))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    obj = kit.from_bmesh(name, bm, m)
    return k.smooth(obj, 50)


def pill(name, x0, x1, y0, y1, z0, lift, m, r=None):
    """A rounded lens over a rectangle: from z0 at its edge to z0 + lift a corner's radius in."""
    r = min(x1 - x0, y1 - y0) / 2 * 0.98 if r is None else r
    outline = rounded_rect(x0, x1, y0, y1, r, 5)
    edge = min(x1 - x0, y1 - y0) / 2
    return piece(name, outline, lambda x, y, d: z0 + lift * ps.rounded(d, edge), m, bottom=z0 - 1.0, step=0.35,
                 edge_step=0.22)


def rod(name, points, radius, m, height=None, ends=(True, True), segments=14, picks=None):
    """A tube along points (x, y, z), its ends rounded over its radius (ps.band; height: its half-height, radius
    its half-width). picks: {key: material} with a pick function, else one material."""
    path = [Vector(p) for p in points]
    length = [0.0]
    for a, b in zip(path, path[1:]):
        length.append(length[-1] + (b - a).length)
    total = length[-1]
    # (More points over the rounded ends: at the cap's own angles, read off the path.)
    wanted = set(round(s, 6) for s in length)
    for i in range(1, 6):
        e = radius * (1 - math.cos(math.radians(90 * i / 6)))
        if e < total / 2:
            if ends[0]:
                wanted.add(round(e, 6))
            if ends[1]:
                wanted.add(round(total - e, 6))
    if len(wanted) > len(length):
        resampled_path = []
        for s in sorted(wanted):
            j = max(0, min(len(length) - 2, bisect.bisect_left(length, s) - 1))
            span = length[j + 1] - length[j]
            t = 0.0 if span < 1e-9 else max(0.0, min(1.0, (s - length[j]) / span))
            resampled_path.append(path[j] + (path[j + 1] - path[j]) * t)
        path = resampled_path
        length = sorted(wanted)
        total = length[-1]
    widths, heights = [], []
    h = radius if height is None else height
    for s in length:
        f = 1.0
        if ends[0] and s < radius:
            f = math.sqrt(max(0.0, 1 - (1 - s / radius) ** 2))
        if ends[1] and total - s < radius:
            f = min(f, math.sqrt(max(0.0, 1 - (1 - (total - s) / radius) ** 2)))
        widths.append(radius * f)
        heights.append(h * f)
    if picks is None:
        return ps.band(name, path, widths, heights, {"*": m}, segments=segments)
    return ps.band(name, path, widths, heights, picks[0], pick=picks[1], segments=segments)


class Shield:
    """A shield's body: its outline and the height of its front, a low ridge down its middle (cx) falling to its
    sides (hw) and rounded at its edge; with rim, a raised border round it (the frame the cores sit in)."""

    def __init__(self, cx, hw, outline, rim=0.0, rim_width=1.5, z_edge=0.7, z_side=1.35, z_ridge=2.35):
        self.cx, self.hw, self.outline = cx, hw, outline
        self.rim, self.rim_width = rim, rim_width
        self.z_edge, self.z_side, self.z_ridge = z_edge, z_side, z_ridge

    def face(self, x, y=0.0):
        """The front inside the rim, before the edge is rounded."""
        u = min(1.0, abs(x - self.cx) / self.hw)
        return self.z_side + (self.z_ridge - self.z_side) * (1 - u ** 1.4)

    def height(self, x, y, d=None):
        """The front, d the distance in from the shield's outline (worked out if not given)."""
        if d is None:
            d = ps.edge_distance((x, y), self.outline)
        z = self.face(x, y)
        if self.rim:
            z += self.rim * (1 - smoothstep(self.rim_width - 0.35, self.rim_width + 0.35, d))
        return self.z_edge + (z - self.z_edge) * ps.rounded(d, 0.75)

    def body(self, m, below=None, band=None):
        """The body; band = (y, material, lift): above y a layer of another material, raised by lift over a
        rounded step at its lower edge (a band across the top)."""
        rings = EDGE_RINGS
        if self.rim:
            w = self.rim_width
            rings = EDGE_RINGS + (w - 0.4, w, w + 0.4)
        if band is None:
            return [piece("body", self.outline, lambda x, y, d: self.height(x, y, d), m, step=0.65, rings=rings)]
        # (Two solids split along y = y_band, both rounded by the distance to the whole outline, so that they meet
        # without a seam; the band rises over a rounded step at its lower edge.)
        y_band, band_mat, lift = band
        lower = piece("body", clip_below(self.outline, y_band), lambda x, y, d: self.height(x, y), m, step=0.65,
                      rings=rings)
        upper = piece("band", clip_above(self.outline, y_band),
                      lambda x, y, d: self.height(x, y) + lift * smoothstep(0.0, 0.45, y - y_band)
                      * ps.rounded(ps.edge_distance((x, y), self.outline), 0.75), band_mat, step=0.45, rings=rings)
        return [lower, upper]


def clip_above(outline, y0):
    """The part of a closed outline above y = y0 (Sutherland-Hodgman against one line), counter-clockwise."""
    return _clip(outline, lambda p: p[1] >= y0, lambda a, b: (a[0] + (b[0] - a[0]) * (y0 - a[1]) / (b[1] - a[1]), y0))


def clip_below(outline, y0):
    return _clip(outline, lambda p: p[1] <= y0, lambda a, b: (a[0] + (b[0] - a[0]) * (y0 - a[1]) / (b[1] - a[1]), y0))


def _clip(outline, keep, cut):
    out = []
    n = len(outline)
    for i in range(n):
        a, b = outline[i], outline[(i + 1) % n]
        if keep(a):
            out.append(a)
            if not keep(b):
                out.append(cut(a, b))
        elif keep(b):
            out.append(cut(a, b))
    clean = []
    for p in out:
        if not clean or math.hypot(p[0] - clean[-1][0], p[1] - clean[-1][1]) > 1e-4:
            clean.append(p)
    if math.hypot(clean[0][0] - clean[-1][0], clean[0][1] - clean[-1][1]) < 1e-4:
        clean.pop()
    return clean


# --- The outlines --------------------------------------------------------------------------------------------------

# The wide shield (153, 157, 159, 163; 165 drawn a column further right): columns 3-18 between its outline's columns
# 2 and 19, its top on row 5, straight sides down to row 16, then in to two points (columns 8 and 13 of row 22) with a
# notch between them under the spine (rows 20-22), drawn narrower here.
WIDE_CX, WIDE_HW = -1.0, 8.6
WIDE_TOP = 8.7


def wide_outline(notch=True):
    cx = WIDE_CX
    left = [(cx, WIDE_TOP), (-9.05, WIDE_TOP), (-9.42, 8.55), (-9.6, 8.15)]
    side = smooth_path([(-9.6, 8.15), (-9.6, -2.3), (-9.38, -4.2), (-8.6, -5.95), (-7.2, -7.55), (-5.5, -8.85),
                        (-3.75, -9.75)], 4)
    left += side[1:]
    if notch:
        # (A narrow slot between the points, as the picture's: wider, the shield read as a spade.)
        left += [(-3.05, -9.98), (-2.55, -9.92), (-2.2, -9.6)]
        left += smooth_path([(-2.2, -9.6), (-1.85, -8.6), (-1.45, -7.75), (cx, -7.35)], 3)[1:]
    else:
        left += smooth_path([(-4.1, -9.55), (-2.9, -10.05), (cx, -10.3)], 3)[1:]
    return mirrored(left, cx)


# The narrow LXS shield (155): columns 4-16 between its outline's 3 and 17, its top on row 5, straight down to row
# 15, in to two points (columns 9 and 11 of row 21) with a slot between (column 10, rows 19-21).
NARROW_CX, NARROW_HW, NARROW_TOP = -1.5, 7.0, 8.6


def narrow_outline():
    cx = NARROW_CX
    left = [(cx, NARROW_TOP), (-8.0, NARROW_TOP), (-8.36, 8.45), (-8.5, 8.1)]
    left += smooth_path([(-8.5, 8.1), (-8.5, -1.8), (-8.25, -3.6), (-7.4, -5.3), (-6.0, -6.9), (-4.4, -8.1),
                         (-3.35, -8.7)], 4)[1:]
    left += [(-2.85, -8.8), (-2.45, -8.55), (-2.2, -8.1)]
    left += smooth_path([(-2.2, -8.1), (-1.9, -6.4), (cx, -5.25)], 3)[1:]
    return mirrored(left, cx)


# The narrow HXS shield (161): columns 5-17 between its outline's 4 and 18, its top on row 6 (the cell box above it),
# straight down to row 17, then round into a U whose bottom is row 23 (a grey foot).
HXS_CX, HXS_HW, HXS_TOP = -0.5, 7.0, 7.5


def hxs_outline():
    cx = HXS_CX
    left = [(cx, HXS_TOP), (-7.0, HXS_TOP), (-7.36, 7.35), (-7.5, 7.0)]
    left += smooth_path([(-7.5, 7.0), (-7.5, -3.4), (-7.25, -5.5), (-6.3, -7.4), (-4.7, -9.0), (-2.7, -10.15),
                         (cx, -10.55)], 4)[1:]
    return mirrored(left, cx)


# --- The wide shield's parts ---------------------------------------------------------------------------------------

def spine(shield, y_top, y_bottom, width=2.2, height=1.55, lift=0.15, neck=8.4, tip=0.42):
    """The ridge down the middle: a rounded bar (its top a lighter crest) from y_bottom (a rounded end) up to the
    shield's top edge, where it narrows (from neck up, to tip of its width) into a short rounded point standing out of
    the edge up to y_top (the picture's two pixels over row 5). (Full width to its end, it read as a spade's handle.)"""
    cx = shield.cx
    cap = width * tip
    ys = set()
    for i in range(7):
        ys.add(round(y_bottom + width * (1 - math.cos(math.radians(90 * i / 6))), 5))
        ys.add(round(y_top - cap * (1 - math.cos(math.radians(90 * i / 6))), 5))
    body0, body1 = y_bottom + width, min(neck, y_top - cap)
    n = max(1, int(math.ceil((body1 - body0) / 0.6)))
    for i in range(n + 1):
        ys.add(round(body0 + (body1 - body0) * i / n, 5))
    for i in range(1, 5):
        ys.add(round(body1 + (y_top - cap - body1) * i / 4, 5))

    def scale(y):
        if y < y_bottom + width:
            return math.sqrt(max(0.0, 1 - (1 - (y - y_bottom) / width) ** 2))
        f = 1.0 - (1.0 - tip) * smoothstep(body1, y_top - cap, y)
        if y > y_top - cap:
            f = tip * math.sqrt(max(0.0, 1 - ((y - (y_top - cap)) / cap) ** 2))
        return f
    path, widths, heights = [], [], []
    for y in sorted(ys, reverse=True):  # (from its top down)
        f = scale(y)
        path.append(Vector((cx, y, shield.z_ridge + lift - height * (1 - f) * 0.5)))
        widths.append(width * f)
        heights.append(height * f)

    def pick(t, a):
        return "crest" if 62 <= a <= 118 else "*"
    return ps.band("spine", path, widths, heights, {"*": M["steel"], "crest": M["steel_light"]}, pick=pick,
                   segments=16)


def cross_bar(shield, y0, y1, m, lift=0.5, inset=1.15, name="bar"):
    """A raised bar across the front between the rims (rounded ends)."""
    x0, x1 = shield.cx - shield.hw + inset, shield.cx + shield.hw - inset
    outline = rounded_rect(x0, x1, y0, y1, min(0.6, (y1 - y0) / 2), 4)
    return piece(name, outline, lambda x, y, d: shield.face(x) + shield.rim * 0.4 + lift * ps.rounded(d, 0.4), m,
                 bottom=shield.z_side - 0.6, step=0.4)


def socket_strip(shield, x0, x1, y0, y1, lift=0.18, name="sockets"):
    outline = rounded_rect(x0, x1, y0, y1, 0.5, 4)
    return piece(name, outline, lambda x, y, d: shield.face(x) + shield.rim * 0.3 + lift * ps.rounded(d, 0.3),
                 M["steel_dark"], bottom=shield.z_side - 0.6, step=0.4)


def lamp(shield, x, y0, y1, w, colour, name="lamp", hot=None):
    """A lamp: a glowing lens in the socket strip; hot: a brighter bead on its lit side."""
    z0 = shield.face(x) + shield.rim * 0.3 + 0.05
    parts = [pill(name, x - w / 2, x + w / 2, y0, y1, z0, 0.75, M[colour])]
    if hot is not None:
        parts.append(k.smooth(k.ellipsoid(name + "_hot", (x - w * 0.18, (y0 + y1) / 2 + 0.25, z0 + 0.62),
                                          (w * 0.26, (y1 - y0) * 0.24, 0.22), M[hot], 12, 8), 70))
    return parts


def core(shield, name, outline, m, lift=1.25, grooves=(), groove_depth=0.55, groove_w=0.45):
    """A glowing core: a lens over the outline, domed, cut by grooves (x positions) down its length; returns its
    parts and its height function (for the ribs on it)."""
    edge = 1.6

    def height(x, y, d):
        z = shield.face(x) + shield.rim * 0.2 + lift * ps.rounded(d, edge)
        for gx in grooves:
            t = abs(x - gx) / groove_w
            if t < 1:
                z -= groove_depth * (1 - t * t) * ps.rounded(d, 0.6)
        return z
    parts = [piece(name, outline, height, m, bottom=shield.z_side - 0.8, step=0.5, rings=EDGE_RINGS + (1.05, 1.45))]
    return parts, height


def ribs(name, height, outline, xs, y_top, y_bottom, m, radius=0.36, raise_=0.12):
    """Glowing ribs down a core (at the xs), following its dome."""
    parts = []
    for i, x in enumerate(xs):
        points = []
        y = y_top
        while y > y_bottom - 1e-6:
            d = ps.edge_distance((x, y), outline)
            points.append((x, y, height(x, y, d) + raise_ - radius * 0.35))
            y -= 0.45
        parts.append(rod("%s_%d" % (name, i), points, radius, m, height=radius * 0.8, segments=8))
    return parts


def nozzle(shield, x, y_top, y_bottom, z, radius=1.15, name="nozzle"):
    """A short grey nozzle lying along y (pointing down the picture): a steel barrel, a dark band, a light tip."""
    points = [(x, y, z) for y in np.linspace(y_top, y_bottom, 9)]
    parts = [rod(name, points, radius, M["steel_light"], height=radius * 0.85, ends=(True, True), segments=16)]
    band_y = y_top - (y_top - y_bottom) * 0.45
    parts.append(rod(name + "_band", [(x, band_y + 0.25, z), (x, band_y - 0.25, z)], radius * 1.06, M["steel_dark"],
                     height=radius * 0.9, ends=(False, False), segments=16))
    return parts


def bead(name, centre, r, m, flat=0.7):
    return k.smooth(k.ellipsoid(name, centre, (r, r, r * flat), m, 14, 9), 70)


def join_by_material(objects):
    """Joins the parts that have one material each, by material (fewer meshes); keeps the order fixed."""
    groups, rest = {}, []
    for obj in objects:
        kit.apply(obj)
        if len(obj.data.materials) == 1:
            groups.setdefault(obj.data.materials[0].name, []).append(obj)
        else:
            rest.append(obj)
    out = []
    for name in sorted(groups):
        objs = groups[name]
        if len(objs) > 1:
            with bpy.context.temp_override(active_object=objs[0], selected_editable_objects=objs, object=objs[0]):
                bpy.ops.object.join()
        objs[0].name = name
        out.append(objs[0])
    return out + rest


# --- The models ----------------------------------------------------------------------------------------------------

def gencore(solar=False):
    """153: Gencore Low and High Energy Shield: the wide heater shield, plain steel, its faces sloping off the spine
    (the left one lit, the right one in shade, as the picture draws them) in a low raised border, its top a bronze
    band (rows 6-9) with gold rivets beside the spine, the spine standing out of its top edge and ending over the
    notch between its two points. solar: the Gencore Solar Shield, the same with a panel of green solar cells in each
    face."""
    s = Shield(WIDE_CX, WIDE_HW, wide_outline(), rim=0.6, rim_width=1.25, z_side=0.9, z_ridge=2.8)
    parts = s.body(M["steel"], band=(4.25, M["bronze"], 0.42))
    parts.append(spine(s, 10.75, -5.55, width=1.75, height=1.3, lift=0.25))
    for x in (s.cx - 3.25, s.cx + 3.25):
        y = 7.15
        parts.append(bead("rivet", (x, y, s.height(x, y) + 0.42), 0.48, M["gold"], 0.8))
    if solar:
        parts += solar_panels(s)
    return parts


def solar_panels(s):
    """A panel of solar cells in each face of the Gencore shield (below its band): dark frames with green cells in
    two columns and three rows, the lower row following the shield's taper."""
    parts = []
    for side in (-1, 1):
        x_in, x_out = s.cx + side * 2.3, s.cx + side * 8.1
        xa, xb = min(x_in, x_out), max(x_in, x_out)
        # The panel: the face between the spine and the rim, rows 10-19, as an inset outline.
        panel = panel_outline(s, xa, xb, 3.55, -6.2, 1.3)
        parts.append(piece("solar_frame", panel, lambda x, y, d: s.face(x) + 0.12 + 0.12 * ps.rounded(d, 0.3),
                           M["steel_dark"], bottom=s.z_side - 0.5, step=0.4))
        cols = 2
        rows = [(3.05, 0.95), (0.55, -1.55), (-1.95, -4.05)]
        w = (xb - xa - 0.5 - 0.3 * (cols - 1)) / cols
        for r, (y1, y0) in enumerate(rows):
            for c in range(cols):
                x0 = xa + 0.25 + c * (w + 0.3)
                cell = clip_to(panel_outline(s, x0, x0 + w, y1, y0, 0.0), panel, 0.32)
                if cell is None:
                    continue
                parts.append(piece("solar_cell", cell, lambda x, y, d: s.face(x) + 0.24 + 0.16 * ps.rounded(d, 0.25),
                                   M["green_solar"], bottom=s.z_side - 0.4, step=0.3))
    return parts


def panel_outline(s, x0, x1, y1, y0, inset):
    """The rectangle x0-x1, y0-y1 cut to the shield's outline less inset (counter-clockwise)."""
    rect = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    return clip_to(rect, s.outline, inset)


def clip_to(poly, outline, inset):
    """A convex poly (a rectangle here) kept at least inset inside outline: its boundary sampled every 0.2, each point
    that is too far out moved towards the poly's centre until it is in (the cells and panels whose lower corner the
    shield's slanted edge cuts). None if too little is left."""
    xs = [p[0] for p in poly]
    ys = [p[1] for p in poly]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    pts = ps.resample(poly, 0.2)
    out = []
    for x, y in pts:
        if ps.inside((x, y), outline) and ps.edge_distance((x, y), outline) >= inset:
            out.append((x, y))
            continue
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        for t in np.linspace(0.0, 1.0, 41)[1:]:
            px, py = x + (cx - x) * t, y + (cy - y) * t
            if ps.inside((px, py), outline) and ps.edge_distance((px, py), outline) >= inset:
                out.append((px, py))
                break
    clean = []
    for p in out:
        if not clean or math.hypot(p[0] - clean[-1][0], p[1] - clean[-1][1]) > 0.08:
            clean.append(p)
    if len(clean) < 4 or abs(ps.area(clean)) < 0.6:
        return None
    return clean


def lxs_a():
    """155: MicroCorp LXS Class A: the narrow shield in a raised frame, three short posts standing out of its top
    edge (its corners and middle), four lamps under them (orange outside, yellow inside), a bar, and a red core
    (rows 9-17) with two orange ribs and a groove between its two lower lobes."""
    s = Shield(NARROW_CX, NARROW_HW, narrow_outline(), rim=0.55, rim_width=1.7)
    parts = s.body(M["steel"])
    cx = s.cx
    # The posts (rows 4-5): the frame's corners and the middle, a pixel over the top edge.
    for x0, x1 in ((-8.5, -6.9), (4.4, 5.5)):
        parts.append(pill("post", x0, x1, 6.4, 9.75, s.height((x0 + x1) / 2, 7.0) - 0.3, 0.7, M["steel_light"], r=0.55))
    parts.append(pill("post_mid", cx - 1.35, cx + 1.35, 5.6, 9.75, s.face(cx) + 0.2, 0.75, M["steel_light"], r=0.6))
    parts.append(socket_strip(s, -6.9, 3.9, 5.75, 8.35))
    for x, colour in ((X(6), "orange"), (X(8), "yellow"), (X(12), "yellow"), (X(14), "orange")):
        parts += lamp(s, x, 5.95, 8.15, 1.35, colour)
    parts.append(cross_bar(s, 4.75, 5.95, M["steel_light"], lift=0.45, inset=1.4))
    outline = smooth_core([(-1.5, 5.05), (-5.8, 5.05), (-6.15, 4.75), (-6.2, -0.6), (-5.6, -2.8), (-4.4, -4.05),
                           (-2.9, -4.15), (-2.15, -3.2), (-1.5, -2.2)], -1.5)
    core_parts, height = core(s, "core", outline, M["red"], lift=1.3, grooves=(cx,), groove_w=0.42,
                              groove_depth=0.3)
    parts += core_parts
    parts += ribs("rib", height, outline, (X(9) + 0.1, X(11) - 0.1), 4.4, -2.0, M["red_rib"])
    parts += ribs("rib_edge", height, outline, (X(6) + 0.55,), 4.3, -1.2, M["red_rib"], radius=0.3)
    return parts


def smooth_core(left, cx, samples=3):
    """A core's outline from its left half (from the top of the centre line down and round to the bottom of the
    centre line), smoothed, mirrored."""
    pts = smooth_path(left, samples)
    return mirrored(pts, cx)


def lxs_b():
    """157: MicroCorp LXS Class B: the wide shield in a raised frame with the full spine; two lamps (rows 6-7), a bar,
    a red core each side of the spine (rows 10-18) with two ribs each, and red vents out through the rim at rows
    11-13."""
    s = Shield(WIDE_CX, WIDE_HW, wide_outline(), rim=0.55, rim_width=1.6)
    parts = s.body(M["steel"])
    parts.append(spine(s, 10.75, -5.55, width=2.1, height=1.75, lift=0.35))
    parts.append(socket_strip(s, -8.0, 6.0, 5.8, 8.4))
    for x in (X(6), X(15)):
        parts += lamp(s, x, 5.95, 8.2, 3.0, "orange", hot="yellow")
    parts.append(cross_bar(s, 4.3, 5.9, M["steel_light"], lift=0.5))
    for side in (-1, 1):
        sx = lambda x: s.cx + side * (x - s.cx)  # noqa: E731  (the left side's x to this side's)
        left = [(-5.0, 4.15), (-6.1, 4.0), (-6.85, 3.3), (-7.0, 1.6), (-7.0, -1.8), (-6.7, -3.6), (-5.9, -4.7),
                (-4.7, -5.1), (-3.6, -4.7), (-3.2, -3.5), (-3.15, 3.2), (-3.6, 3.95)]
        outline = [(sx(x), y) for x, y in left]
        if side > 0:
            outline = list(reversed(outline))
        core_parts, height = core(s, "core", outline, M["red"], lift=1.15, grooves=(sx(-5.05),), groove_w=0.42)
        parts += core_parts
        parts += ribs("rib", height, outline, (sx(-6.05), sx(-3.95)), 3.4, -3.6, M["red_rib"], radius=0.32)
        # The vent through the rim (rows 11-13): a glowing block standing a little out of the shield's side.
        x_out = s.cx + side * (s.hw + 0.35)
        x_in = s.cx + side * (s.hw - 2.6)
        xa, xb = min(x_out, x_in), max(x_out, x_in)
        parts.append(pill("vent", xa, xb, 0.35, 2.75, s.z_edge + 0.1, s.face(xa) + s.rim - s.z_edge + 0.35, M["red"],
                          r=0.7))
        parts.append(pill("vent_hot", min(x_out, x_in + side * 0.8), max(x_out, x_in + side * 0.8), 1.15, 2.35,
                          s.face(xa) + s.rim * 0.8, 0.35, M["red_rib"], r=0.45))
    return parts


def lxs_c():
    """159: MicroCorp LXS Class C: the wide shield in a raised frame, the spine only down to the bar, four lamps, and
    one wide red core (rows 10-18) with four ribs and a hot spot at its top, its two lower lobes either side of a
    grey nozzle."""
    s = Shield(WIDE_CX, WIDE_HW, wide_outline(), rim=0.55, rim_width=1.6)
    parts = s.body(M["steel"])
    parts.append(spine(s, 10.75, 4.6, width=2.1, height=1.7, lift=0.35))
    parts.append(socket_strip(s, -8.0, 6.0, 5.8, 8.4))
    for x, colour in ((X(5), "orange"), (X(7), "yellow"), (X(14), "yellow"), (X(16), "orange")):
        parts += lamp(s, x, 5.95, 8.2, 1.35, colour)
    parts.append(cross_bar(s, 4.3, 5.9, M["steel_light"], lift=0.5))
    cx = s.cx
    outline = smooth_core([(cx, 4.15), (-6.3, 4.15), (-6.95, 3.6), (-7.05, 1.5), (-7.0, -2.3), (-6.6, -4.1),
                           (-5.7, -5.05), (-4.4, -5.25), (-3.4, -4.6), (-2.9, -3.3), (-2.2, -2.75), (cx, -2.7)], cx)
    core_parts, height = core(s, "core", outline, M["red"], lift=1.35, grooves=(cx - 2.6, cx + 2.6), groove_w=0.42)
    parts += core_parts
    parts += ribs("rib", height, outline, (cx - 4.6, cx - 1.35, cx + 1.35, cx + 4.6), 3.5, -2.2, M["red_rib"],
                  radius=0.33)
    parts.append(bead("hot", (cx, 3.0, height(cx, 3.0, ps.edge_distance((cx, 3.0), outline)) + 0.05),
                      0.95, M["yellow"], 0.45))
    parts += nozzle(s, cx, -2.0, -5.6, s.face(cx) + 0.75, radius=1.1)
    return parts


def hxs_a():
    """161: MicroCorp HXS Class A: the narrow round-footed shield in a raised frame, a box over its top edge holding
    a green cell (rows 3-6) over a grey block with two bolts, green strips beside it, a dark bar, a green core (rows
    11-19) with three pale ribs, a red lamp at its lower left, and a grey cap on its round foot (rows 20-23)."""
    s = Shield(HXS_CX, HXS_HW, hxs_outline(), rim=0.55, rim_width=1.6)
    parts = s.body(M["steel"])
    cx = s.cx
    # The box on the top edge (columns 6-16, rows 3-8).
    box_z = s.face(cx) + 0.55
    box = rounded_rect(-6.4, 5.4, 4.6, 10.45, 0.7, 5)
    parts.append(piece("box", box, lambda x, y, d: box_z + 0.4 * ps.rounded(d, 0.45), M["steel_dark"],
                       bottom=s.z_side - 0.6, step=0.4))
    parts.append(pill("cell", cx - 2.55, cx + 2.55, 7.15, 10.05, box_z + 0.3, 0.8, M["green_cell"], r=0.9))
    parts.append(pill("block", cx - 2.45, cx + 2.45, 5.0, 7.25, box_z + 0.3, 0.55, M["steel"], r=0.55))
    for x in (X(10), X(12)):
        parts.append(bead("bolt", (x, 6.2, box_z + 0.85), 0.5, M["steel_light"], 0.7))
    for x in (X(7), X(15)):
        parts.append(pill("strip", x - 0.55, x + 0.55, 5.4, 9.7, box_z + 0.3, 0.45, M["green_cell"], r=0.5))
    # The dark bar (rows 9-10) and the core.
    parts.append(cross_bar(s, 3.1, 4.75, M["steel_dark"], lift=0.35, inset=1.3, name="bar"))
    outline = smooth_core([(cx, 2.95), (-4.55, 2.95), (-5.0, 2.5), (-5.05, -1.0), (-4.8, -3.9), (-4.1, -5.4),
                           (-2.9, -6.05), (cx, -6.2)], cx)
    core_parts, height = core(s, "core", outline, M["green"], lift=1.3, grooves=(cx - 1.1, cx + 1.1), groove_w=0.42)
    parts += core_parts
    parts += ribs("rib", height, outline, (cx - 2.5, cx, cx + 2.5), 2.4, -4.9, M["green_rib"], radius=0.3)
    parts.append(bead("lamp", (X(8), Y(19) + 0.25, s.face(X(8)) + 0.85), 0.62, M["red_dot"], 0.7))
    # The foot: a light band (row 20) and a rounded cap (rows 21-23).
    foot = smooth_core([(cx, -6.45), (-4.6, -6.45), (-4.75, -6.9), (-4.2, -8.0), (-3.1, -9.15), (-1.8, -9.75),
                        (cx, -9.95)], cx)
    parts.append(piece("foot", foot, lambda x, y, d: s.face(x) + 0.35 + 0.75 * ps.rounded(d, 1.4) *
                       (0.75 + 0.25 * smoothstep(-9.9, -7.0, y)), M["steel_light"], bottom=s.z_side - 0.6, step=0.35))
    return parts


def hxs_top(s, split=False, tall=False):
    """The top of the wide HXS shields (163, 165): a green cell in a dark housing in each top corner, standing a
    pixel or two out of the top edge, and a green arch over the spine's top (split: two quarter arches either side of
    it, each ending in a cap)."""
    parts = []
    y_top = 10.45 if tall else 9.95
    for side in (-1, 1):
        x = s.cx + side * 5.5
        z = s.face(x) + s.rim * 0.3
        parts.append(pill("housing", x - 1.45, x + 1.45, 5.75, y_top, z, 0.85, M["steel_dark"], r=0.6))
        parts.append(pill("cell", x - 0.62, x + 0.62, 6.4, y_top - 0.55, z + 0.55, 0.55, M["green_cell"], r=0.55))
    z = s.z_ridge + 1.2
    r = 0.78
    if not split:
        pts = [(s.cx - 3.0, 5.6, z - 0.2), (s.cx - 3.0, 8.0, z), (s.cx - 2.7, 9.6, z + 0.25),
               (s.cx - 1.6, 10.35, z + 0.4),
               (s.cx, 10.5, z + 0.45)]
        pts += [(2 * s.cx - x, y, zz) for x, y, zz in reversed(pts[:-1])]
        path = [tuple(p) for p in ps.catmull(pts, 4)]
        parts.append(rod("arch", path, r, M["green_cell"], height=r * 0.9, segments=12))
    else:
        for side in (-1, 1):
            pts = [(s.cx + side * 3.0, 5.6, z - 0.2), (s.cx + side * 3.0, 8.0, z), (s.cx + side * 2.75, 9.6, z + 0.25),
                   (s.cx + side * 1.95, 10.3, z + 0.35)]
            path = [tuple(p) for p in ps.catmull(pts, 4)]
            parts.append(rod("arch", path, r, M["green_cell"], height=r * 0.9, segments=12))
            parts.append(bead("arch_cap", (s.cx + side * 1.75, 10.35, z + 0.35), 0.62, M["steel_light"], 0.9))
    return parts


def hxs_core(s, nozzle_in_core=False):
    """The wide HXS core (rows 10-18): green, two pale ribs each side of a groove, its two lower lobes either side of a
    grey nozzle; nozzle_in_core: another nozzle in its middle (165)."""
    cx = s.cx
    outline = smooth_core([(cx, 4.15), (-6.3, 4.15), (-6.95, 3.6), (-7.05, 1.5), (-7.0, -2.3), (-6.6, -4.1),
                           (-5.7, -5.05), (-4.4, -5.25), (-3.4, -4.6), (-2.9, -3.3), (-2.2, -2.75), (cx, -2.7)], cx)
    grooves = (cx - 3.0, cx + 3.0) if nozzle_in_core else (cx,)
    core_parts, height = core(s, "core", outline, M["green"], lift=1.3, grooves=grooves, groove_w=0.45)
    parts = list(core_parts)
    xs = (cx - 4.6, cx - 1.6, cx + 1.6, cx + 4.6) if not nozzle_in_core else (cx - 4.7, cx - 1.6, cx + 1.6, cx + 4.7)
    parts += ribs("rib", height, outline, xs, 3.5, -2.2, M["green_rib"], radius=0.32)
    parts += nozzle(s, cx, -2.0, -5.6, s.face(cx) + 0.75, radius=1.1)
    if nozzle_in_core:
        parts += nozzle(s, cx, 2.35, -1.15, s.face(cx) + 1.55, radius=1.05, name="nozzle_core")
        parts.append(pill("socket", cx - 1.35, cx + 1.35, 1.9, 3.35, s.face(cx) + 0.95, 0.55, M["black"], r=0.55))
    parts.append(bead("lamp", (s.cx - 3.5, -4.4, s.face(s.cx - 3.5) + 1.2), 0.62, M["red_dot"], 0.7))
    return parts


def hxs_b():
    """163: MicroCorp HXS Class B: the wide shield in a raised frame, the spine's top under a green arch, a green cell
    in each top corner, a light bar (row 8), a wide green core, grey clamps on the rim at rows 12-14."""
    s = Shield(WIDE_CX, WIDE_HW, wide_outline(), rim=0.55, rim_width=1.6)
    parts = s.body(M["steel"])
    parts.append(spine(s, 9.85, 4.6, width=2.1, height=1.6, lift=0.3))
    parts += hxs_top(s)
    parts.append(cross_bar(s, 4.3, 5.9, M["steel_light"], lift=0.5))
    parts += hxs_core(s)
    for side in (-1, 1):
        x_out = s.cx + side * (s.hw + 0.25)
        x_in = s.cx + side * (s.hw - 1.7)
        parts.append(pill("clamp", min(x_out, x_in), max(x_out, x_in), -0.45, 1.35, s.z_edge + 0.2,
                          s.face(min(x_out, x_in)) + s.rim + 0.35 - s.z_edge, M["steel_light"], r=0.5))
    return parts


def hxs_c():
    """165: MicroCorp HXS Class C: as 163, the arch split by the spine's top into two quarter arches, the corner cells
    taller, and a second nozzle in the core's middle (no clamps)."""
    s = Shield(WIDE_CX, WIDE_HW, wide_outline(), rim=0.55, rim_width=1.6)
    parts = s.body(M["steel"])
    parts.append(spine(s, 10.75, 4.6, width=2.1, height=1.7, lift=0.35))
    parts += hxs_top(s, split=True, tall=True)
    parts.append(cross_bar(s, 4.3, 5.9, M["steel_light"], lift=0.5))
    parts += hxs_core(s, nozzle_in_core=True)
    return parts


# --- The integrity fields (129, 131) -------------------------------------------------------------------------------

BALL_C = (-1.5, 1.6, 0.0)
BALL_R = (7.45, 7.35, 5.6)


def lobed_ball(name, centre, radii, lobes, depth, mats, seam_width=0.10, segments=96, rings=40):
    """An ellipsoid round its y axis (the picture's up), its surface in `lobes` gores bulging by depth between
    seams; mats: (gore, seam) materials, the seam the faces nearest each seam."""
    import bmesh
    cx, cy, cz = centre
    rx, ry, rz = radii
    bm = bmesh.new()
    rows = []
    for i in range(1, rings):
        t = math.pi * i / rings
        yy = cy + ry * math.cos(t)
        s = math.sin(t)
        row = []
        for j in range(segments):
            phi = 2 * math.pi * j / segments  # 0 towards the viewer (+z)
            g = abs(math.cos(lobes * phi / 2))  # 1 mid-gore, 0 at a seam
            bulge = 1 + depth * (g ** 0.5 - 0.6)
            row.append(bm.verts.new((cx + rx * s * math.sin(phi) * bulge, yy, cz + rz * s * math.cos(phi) * bulge)))
        rows.append(row)
    top = bm.verts.new((cx, cy + ry, cz))
    bottom = bm.verts.new((cx, cy - ry, cz))
    seam_faces = set()
    n = segments
    for i in range(len(rows) - 1):
        for j in range(n):
            f = bm.faces.new((rows[i][j], rows[i][(j + 1) % n], rows[i + 1][(j + 1) % n], rows[i + 1][j]))
            phi = 2 * math.pi * (j + 0.5) / n
            if abs(math.cos(lobes * phi / 2)) < math.sin(math.pi * seam_width):
                seam_faces.add(f)
    for j in range(n):
        bm.faces.new((top, rows[0][(j + 1) % n], rows[0][j]))
        bm.faces.new((bottom, rows[-1][j], rows[-1][(j + 1) % n]))
    for f in bm.faces:
        f.material_index = 1 if f in seam_faces else 0
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    obj = kit.from_bmesh(name, bm)
    obj.data.materials.append(mats[0])
    obj.data.materials.append(mats[1])
    return k.smooth(obj, 60)


def integrity_field(advanced=False):
    """129: Structural Integrity Field: a ball of blue glass (rows 4-17) round a glowing blue core, set in a grey
    base: an emitter in front of its foot (columns 8-12, rows 14-20) with two dark slots and a lens, a base plate under
    it and a rounded foot either side (columns 3-6 and 14-17, rows 18-21). advanced (131: Advanced Integrity Field):
    the ball bronze, in eight gores between dark seams, the feet wider and taller (columns 1-5 and 15-19, rows
    17-22)."""
    parts = []
    cx, cy, cz = BALL_C
    if advanced:
        parts.append(lobed_ball("ball", BALL_C, BALL_R, 8, 0.06, (M["bronze"], M["bronze_dark"]), seam_width=0.07))
    else:
        # Deep blue glass lit from inside: in bands by its slope (psr.ball), dark at its rim, lighter towards its
        # middle (as the picture shades it), a white glint up to the left (its highlight, rows 7-10). (Opaque: a
        # see-through shell shadowed itself in speckles; glow_spot's patches had ragged edges.)
        parts.append(psr.ball("ball", BALL_C, BALL_R, [M["glass"], M["field"], M["field_hot"]], [0.55, 0.88], 64, 36))
        parts += a.glow_spot("glint", BALL_C, BALL_R, (cx - 3.2, cy + 2.9), [(1.25, 0.32, M["glint"])], 72, 36)
    # The base plate (rows 21-22) under the emitter, from foot to foot.
    plate = rounded_rect(-6.6, 3.6, -9.0, -5.2, 1.1, 5)
    parts.append(piece("plate", plate,
                       lambda x, y, d: 0.9 + 0.75 * ps.rounded(d, 0.8) - 0.3 * smoothstep(-6.8, -5.2, y),
                       M["steel_mid"], bottom=-1.0, step=0.5))
    feet = ((-9.4, -5.8), (2.8, 6.4)) if not advanced else ((-10.9, -6.7), (3.7, 7.9))
    y0, y1 = (-8.4, -4.2) if not advanced else (-9.2, -3.1)
    height = 2.6 if not advanced else 3.1
    for x0, x1 in feet:
        foot = rounded_rect(x0, x1, y0, y1, 1.5, 6)
        xm = (x0 + x1) / 2
        parts.append(piece("foot", foot, lambda x, y, d: 0.6 + (height - 0.6) * ps.rounded(d, 1.6),
                           M["steel"], bottom=-1.0, step=0.5, rings=EDGE_RINGS + (1.3, 1.6)))
        parts.append(pill("foot_top", xm - (x1 - x0) * 0.24, xm + (x1 - x0) * 0.24, y0 + 1.3, y1 - 1.3, height - 0.35,
                          0.4, M["steel_light"], r=0.5))
    # The emitter (columns 8-12, rows 14-20): a block standing out of the ball's foot, its front slotted, a lens
    # between the slots.
    ex0, ex1 = X(8) - 0.45, X(12) + 0.45
    emitter = rounded_rect(ex0, ex1, -7.0, 0.6, 0.7, 5)
    front = 5.8

    def emitter_z(x, y, d):
        return front - 0.8 + 0.8 * ps.rounded(d, 0.7) - 0.9 * smoothstep(-2.0, 0.6, y)
    parts.append(piece("emitter", emitter, emitter_z, M["steel_light"], bottom=0.0, step=0.4))
    for yc in (Y(15), Y(19)):
        parts.append(piece("slot", rounded_rect(ex0 + 0.75, ex1 - 0.75, yc - 0.4, yc + 0.4, 0.35, 3),
                           lambda x, y, d: emitter_z(x, y, 2.0) + 0.04 + 0.08 * ps.rounded(d, 0.2), M["black"],
                           bottom=front - 2.2, step=0.25))
    parts.append(pill("emitter_lens", X(10) - 1.1, X(10) + 1.1, -4.9, -2.75, front - 0.05, 0.4,
                      M["field"] if not advanced else M["gold"], r=0.6))
    return parts


MODELS = [
    ("store_shield_129", 129, lambda: integrity_field(False), 0),
    ("store_shield_131", 131, lambda: integrity_field(True), 0),
    ("store_shield_153", 153, lambda: gencore(False), 0),
    ("store_shield_155", 155, lxs_a, 0),
    ("store_shield_157", 157, lxs_b, 0),
    ("store_shield_159", 159, lxs_c, 0),
    ("store_shield_161", 161, hxs_a, 0),
    ("store_shield_163", 163, hxs_b, 0),
    ("store_shield_165", 165, hxs_c, 1),   # (its picture a column further right than the other wide ones)
    ("store_shield_solar", 153, lambda: gencore(True), 0),
]


# --- Checks and previews -------------------------------------------------------------------------------------------

def picture_mask(directory, picture):
    """The picture's object pixels: everything drawn but its outline's colour (12, 4, 0) and the shadow's (24, 12,
    0) (the outline is the object's edge: the model reaches half way into it)."""
    path = os.path.join(directory, "shop_%d.png" % picture)
    image = bpy.data.images.load(path)
    w, h = image.size
    px = np.array(image.pixels[:]).reshape(h, w, 4)[::-1]
    bpy.data.images.remove(image)
    rgb = np.round(px[:, :, :3] * 255).astype(int)
    out = []
    for y in range(h):
        row = []
        for x in range(w):
            r, g, b = rgb[y, x]
            row.append(px[y, x, 3] > 0.5 and (r, g, b) not in ((12, 4, 0), (24, 12, 0)))
        out.append(row)
    return out


def icon_view(prefix, objects, background=(52, 44, 36)):
    """The icon renderer's view (render_gpu.c icon_render): the camera below the picture's bottom edge and to its
    right, 55 degrees up, the picture's up towards the image's upper right; the sun as the game's, from the upper left
    of the screen (in the model's frame: from its lower left and above)."""
    scene = bpy.context.scene
    before = set(bpy.data.objects)
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.film_transparent = True
    scene.view_settings.view_transform = "Standard"
    world = bpy.data.worlds.new("icon")
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.42, 0.44, 0.5, 1)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.7
    scene.world = world
    sun = bpy.data.lights.new("icon_sun", "SUN")
    sun.energy = 3.2
    sun_obj = bpy.data.objects.new("icon_sun", sun)
    sun_obj.rotation_euler = Vector((0.478, 0.372, -1.163)).to_track_quat("-Z", "Y").to_euler()
    scene.collection.objects.link(sun_obj)
    low, high = kit.bounds(objects)
    centre = (low + high) / 2
    radius = (high - low).length / 2
    direction = Vector((0.287, -0.497, 0.819)).normalized()
    up = Vector((-0.41, 0.709, 0.574)).normalized()
    data = bpy.data.cameras.new("icon_cam")
    data.lens_unit = "FOV"
    data.angle = math.radians(20)
    data.clip_end = 2000
    cam = bpy.data.objects.new("icon_cam", data)
    cam.location = centre + direction * radius / math.tan(math.radians(10)) * 1.02
    forward = -direction
    right = forward.cross(up).normalized()
    true_up = right.cross(forward).normalized()
    cam.matrix_world = Matrix((
        (right.x, true_up.x, -forward.x, cam.location.x),
        (right.y, true_up.y, -forward.y, cam.location.y),
        (right.z, true_up.z, -forward.z, cam.location.z),
        (0, 0, 0, 1)))
    scene.collection.objects.link(cam)
    scene.camera = cam
    scene.render.resolution_x = scene.render.resolution_y = 512
    scene.render.filepath = prefix + "_icon.png"
    bpy.ops.render.render(write_still=True)
    for obj in set(bpy.data.objects) - before:
        bpy.data.objects.remove(obj)


def build():
    opts = kit.options()
    for name, picture, make, shift in MODELS:
        if not kit.wanted(opts, name):
            continue
        k.reset()
        M.clear()
        M.update(materials())
        parts = make()
        parts = join_by_material(parts)
        for obj in parts:
            kit.drop_unused_materials(obj)
        ps.triangulate(parts)
        bpy.context.view_layer.update()
        if "check" in opts:
            kit.compare("%s (picture %d)" % (name, picture), kit.coverage(parts, 24, 28, shift=(shift, 0.0)),
                        picture_mask(opts["check"], picture))
        bpy.context.scene.view_settings.view_transform = "Standard"
        kit.report(name, parts, os.path.join(kit.outdir(opts), name + ".glb"))
        if "preview" in opts:
            kit.preview(opts["preview"] + name, parts, (24, 28), scale=16, distance=0.75)
            icon_view(opts["preview"] + name, parts)


if __name__ == "__main__":
    build()
