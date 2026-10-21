"""The blue gate of BRAINIAC, ICE EXIT and ICESECRET (and episode 6's GLACIER and CRUSTGATE): sheet ^ (x5e in
models.cfg) sprites 16, 18 above 54, 56, 2x2 each: one 48 x 56 picture; enemies 412, 413 above 414, 415 of episode 4
and 1653, 1650 above 1651, 1652 of episode 6, in the sky; one frame each, not animated (ani 1, animate 0, and no
level event starts an animation). Polished 2026-10-21; it replaces wave3_i.py's gate_whole() (regions of the sprite's
pixels raised into blobs). models.cfg: model blue_gate_tl / _tr / _bl / _br enemies/blue_gate_*.glb origin
(unchanged); sprite x5e 16 blue_gate_tl yaw=0 and the same for 18, 54, 56 (unchanged). No other enemy (launched ones
included) shows these sprites; none of them is another sprite's pixels mirrored, turned or in other ramps. The
picture is its own mirror image in coverage about the middle of column 24 (column c is column 48 - c; 99 % of its
pixels), not in its shades (lit from the upper left).

The levels always place the four as one picture (event 15, sky enemies, link 189 or 1-4): 412 (16) and 413 (18) 24
pixels apart, 28 pixels above 414 (54) and 415 (56) at the same x (ICE EXIT t 3600 and BRAINIAC 5100 at x 110 / 134;
ICESECRET 14 times, 13 of them at x 10 / 34 or 210 / 234 coming down with vy 1 (t 140-280, 2540-2680, 11100-11299),
one at t 10600 at 110 / 134; GLACIER 2400 and CRUSTGATE 6000 as BRAINIAC's). The lower two fire (414 and 415: weapon
142 every 60 ticks).

As the sprites and their 4x upscales draw it (columns and rows of the 48 x 56 picture; the right half is the left one
mirrored): an organic blue body (ramp 3, outlined black) shaped like a lyre: two tall horns (columns 6-20 of rows
0-15: a teardrop, its tip at column 12, row 0, widest at rows 8-14, lit along its left edge, a light ridge down its
middle (column 14, rows 2-12), a groove down its left side (column 9, rows 8-16) that turns in along row 11 and down
again beside a light ridge (columns 12-13, rows 11-21), a small bulb on its inner side (columns 18-20 of rows 10-14));
under each horn a grey bracket clamped round the arm (columns 4-14 of rows 16-22: a frame sticking out to the left, a
dark window in it with the arm's blue showing through, its right side a bright bar); the arms going on down (rows
22-35): an outer part (columns 8-11) and an inner one (columns 14-21, a crease down it, a lit knob at its top,
columns 19-20 of rows 23-25) either side of a grey strut that runs down from the bracket (columns 12-13), bends in
through a grey collar where the arm meets the bowl (columns 11-15 of rows 32-36) and goes on down the bowl's inner
wall (columns 15-16 of rows 37-44); the bowl (rows 36-53): its walls (columns 9-17), its bottom curving round (rows
44-53), a light lip along its front middle (columns 20-28 of rows 49-51), two small light blobs on its inner rim
(columns 18-20 and 28-30 of rows 45-47); between them, in the middle of the inner rim, the emitter (columns 22-26 of
rows 44-47: a grey cup with a white-hot point) and the spike rising from it up the screen (columns 21-27 of rows
36-43: a bud of two lit lobes with a dark crease between them, on a dark neck, rows 42-43). Between the arms and round
the spike the sky shows through.

Built as reliefs and machined parts: the blue body is one solid over its outline (polish_ring_machine.relief()'s
method, feature_relief() below: a top rising from a low wall along the outline as a quarter circle, the horns domed
over that, bulbs, knobs and ridges raised and grooves, creases and the strut's channel sunk as smooth fields, a flat
underside; the top triangulated over rows of points laid along the outline, the grooves, the ridges and the channel,
as polish_fire_gate.py's housing, so that they come out smooth), painted along smooth borders: the outline's band,
the grooves, the creases and the channel dark, the ridges, the blobs and the lip light, and by how its top faces the
sun (lit where it is turned to the upper left, shaded where it is turned away), as the sprite paints it; the brackets
bevelled frames (exact booleans) round the arms, the struts flat bars laid in their channels along the body's
surface, the collars bevelled blocks; the spike a bud turned about an axis leaning back up the screen (the oblique view
draws its tip up the screen; from above it covers what the sprite draws, the game's camera sees its front), its
cross-section two lobes with a crease between them, on a dark neck; the emitter a grey cup with a glowing core. The
left half's brackets, struts and collars are built and mirrored about x = 0.5; the body, the spike and the emitter
are built whole. Faces of the machined parts are painted by how they face (tops 0x6a, faces turned to the sun 0x07,
the others 0x04, undersides 0x02). The blues glow a little in their own colours so that the shaded body does not read
black from the game's slanted camera (the body 0x38 0.12, its shaded band and outline 0x35 0.08, its lit band 0x3a
0.14, the ridges, blobs and lip 0x3c 0.2, the spike 0x39 0.16; grooves 0x32 and the spike's crease and neck 0x31 do
not glow); the emitter's core 0x0a 0.6. Height: the body rises to 8.5 (the horns), the brackets to 7.5; all of it
under 9.5, so that from the sky layer (22) it stays under background 3 (32) in BRAINIAC, the one of these levels that
has one. The whole is cut along the sprites' edges (x = 0, y = 0; polish_savara_boss.cut, which keeps each face's
winding: the pieces keep the whole's shading across the cuts, their cuts capped dark), each piece moved so that its
sprite's centre is its origin, its parts joined into one mesh and triangulated (the same output with and without
--check).

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera (z = 0 the base,
on the sky layer); the whole's origin is the middle of the picture (the corner where the four sprites meet): column
c's left edge is x = c - 24, row r's top edge y = 28 - r. The pieces' centres: 16 (-12, 14), 18 (12, 14), 54
(-12, -14), 56 (12, -14).

Replaces wave3_i.py's gate: remove GATE, gate_whole(), the w.WHOLES["gate"] entry and the loop registering
blue_gate_tl ... _br, the blue_gate line of its docstring and "gate," in its --whole usage line; and wave3_i_art.py's
GATE (only gate_whole() reads it). wave3_i.py's region(), GREY and RED stay (the ring, the rock machine and the
spiked hands use them; wave3_ap_surface.py kit.loads wave3_i for sand_whole() and art.SAND).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouettes of the whole
and of each piece against enemy_x5e.png), --preview <prefix> (the whole's top and 3/4 views; --pieces 1 also each
piece's), --only <name,...> (pieces to export; "none": none), --whole <file.glb> (the uncut gate as well, for looking
at), --stats 1 (the whole's parts' triangles).
"""
import math
import os
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector, geometry

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k  # noqa: E402
import polish_deli_boss as db  # noqa: E402  (join, drop_unused)
from polish_savara_boss import cut  # noqa: E402  (polish_arch.cut keeping each face's winding)
from polish_k_pod import triangulate  # noqa: E402
from polish_orb_red import band_split  # noqa: E402
from polish_ring_machine import round_edge, ccw, chaikin, resample, Region  # noqa: E402
from polish_sphere_nozzle import split_along  # noqa: E402
from polish_fire_gate import Thinned, open_resample, offset_curve  # noqa: E402

PIECES = [("blue_gate_tl", 16, (-24.0, 0.0, 0.0, 28.0)), ("blue_gate_tr", 18, (0.0, 24.0, 0.0, 28.0)),
          ("blue_gate_bl", 54, (-24.0, 0.0, -28.0, 0.0)), ("blue_gate_br", 56, (0.0, 24.0, -28.0, 0.0))]
SPRITE_CELLS = {16: (0, 0), 18: (24, 0), 54: (0, 28), 56: (24, 28)}

AX = 0.5                        # the gate's axis (the middle of column 24)
LIGHT = Vector((-0.6, 0.6, 1.0)).normalized()   # towards the sun


def XE(c):
    return c - 24.0


def YE(r):
    return 28.0 - r


def P(c, r):
    return (XE(c), YE(r))


def MX(x):
    return 2 * AX - x


# --- The measures (the left half; pixel edges (column, row)) ----------------------------------------------------------
# The body's outline: from the bottom's middle round the outer side of the left half, round the horn's tip and down its
# inner side to the inner rim's middle.
OUTLINE_LEFT = [(24.5, 54.0), (21.5, 53.9), (18.0, 53.4), (15.2, 52.6), (13.6, 51.4), (12.5, 49.8), (11.6, 48.0),
                (10.8, 46.2), (10.2, 44.5), (10.0, 42.0), (9.6, 40.0), (9.1, 38.0), (9.2, 36.2), (9.8, 34.5),
                (9.9, 32.5), (9.3, 30.5), (8.6, 28.5), (8.0, 26.5), (7.4, 24.5), (7.2, 22.0), (7.0, 18.0),
                (6.8, 15.8), (6.2, 14.0), (6.0, 10.0), (6.1, 6.0), (6.5, 4.3), (7.2, 2.8), (8.2, 1.6), (9.4, 0.6),
                (11.0, 0.05), (12.5, 0.0), (14.0, 0.1), (15.0, 0.8), (15.8, 2.4), (16.6, 4.2), (17.5, 6.0),
                (18.4, 8.0), (19.0, 9.5), (20.2, 10.0), (21.0, 11.0), (21.1, 12.6), (20.9, 14.2), (20.2, 15.0),
                (19.8, 16.0), (19.9, 18.0), (20.0, 21.0), (20.8, 22.2), (21.8, 23.2), (22.0, 25.0), (22.0, 28.6),
                (21.3, 30.0), (21.0, 32.0), (21.0, 35.0), (20.4, 36.2), (19.2, 37.0), (18.3, 38.0), (18.0, 40.0),
                (18.0, 43.4), (18.6, 44.2), (20.0, 44.5), (21.5, 44.6), (24.5, 44.7)]
EDGE_Z = 0.55                   # the low wall along the outline
BODY_Z = 4.7                    # the body's height where nothing raises it
EDGE_R = 3.0                    # the radius its top rounds down to the outline with
# The horn's dome: middle, half-axes, how much higher; the bumps: (middle, half-axes, height) in pixel centres
# (column, row); grooves and ridges: polylines (column, row), depth or height, half-width.
HORN = ((12.0, 10.5), (6.6, 10.8), 3.4)
BUMPS = [((13.0, 19.5), (5.0, 4.5), 1.0),      # the arm under the bracket
         ((19.5, 12.0), (1.5, 2.2), 1.3),      # the horn's bulb
         ((19.5, 24.5), (1.3, 1.5), 2.0),      # the inner part's knob
         ((17.8, 26.5), (3.2, 4.5), 1.2),      # the inner part
         ((10.0, 26.0), (1.8, 4.5), 0.8),      # the outer part
         ((13.2, 40.5), (2.8, 4.2), 0.7),      # the bowl's wall
         ((24.0, 49.8), (3.0, 1.6), 0.35),     # the bowl's front middle (the lip; mirrored onto itself)
         ((19.0, 46.0), (1.4, 1.1), 1.0)]      # the blob on the inner rim
GROOVES = [([(9.5, 7.5), (9.4, 16.5)], 0.9, 0.42),        # down the horn's left side
           ([(9.5, 11.4), (12.6, 11.5)], 0.75, 0.38),      # turning in
           ([(13.5, 11.9), (13.6, 16.6)], 0.75, 0.38),     # and down
           ([(17.6, 9.8), (17.7, 14.4)], 0.9, 0.4),        # round the bulb
           ([(17.4, 22.8), (17.6, 29.5)], 0.7, 0.38),      # the crease down the inner part
           ([(9.0, 35.9), (12.5, 36.3), (16.5, 36.2), (20.0, 35.8)], 2.2, 0.55)]   # where the arm meets the bowl
RIDGES = [([(14.0, 2.2), (14.4, 6.0), (14.6, 12.0)], 0.4, 0.55),   # down the horn's middle
          ([(12.5, 11.8), (12.4, 21.6)], 0.45, 0.5),               # beside the turned groove
          ([(13.4, 37.2), (13.2, 44.0)], 0.35, 0.5)]               # down the bowl's wall
LIP = ((24.5, 50.0), (3.6, 1.05))  # the light lip along the bowl's front middle
# The strut: its path (pixel centres), half-width, how far it stands out of its channel; the channel's depth.
STRUT = [(14.6, 17.4), (13.8, 21.5), (13.0, 23.5), (13.0, 29.0), (13.9, 31.8), (14.8, 34.0), (15.6, 36.6),
         (16.0, 39.0), (16.0, 44.2)]
STRUT_W, STRUT_UP, CHANNEL_D = 1.08, 0.7, 2.5
CHANNEL_W = STRUT_W + 0.55      # the channel's half-width (painted dark)
RIM_W = 0.42                    # the dark band along the outline (the sprite's outline)
LIT_MIN, SHADE_MAX = 0.9, 0.38  # the body's top lit where it faces the sun more than this, shaded under the other
# The bracket: its frame (columns, rows) and the window through it; its height.
BRACKET = (4.0, 15.1, 16.2, 21.9)
BRACKET_WINDOW = (6.9, 13.5, 17.7, 20.8)
BRACKET_Z = (0.3, 7.5)
# The collar where the arm meets the bowl (columns, rows, height).
COLLAR = (10.8, 15.8, 31.9, 36.3, 5.9)
# The spike: its foot and tip (column, row of the axis' ends and their heights), its profile along the axis (t,
# radius), the crease; the emitter (column, row, radius, height).
SPIKE_FOOT, SPIKE_TIP = (24.5, 44.3, 1.6), (24.5, 36.3, 7.2)
SPIKE_PROFILE = [(0.0, 1.15), (0.14, 1.2), (0.26, 1.55), (0.36, 2.7), (0.48, 3.4), (0.58, 3.45), (0.7, 2.95),
                 (0.82, 2.0), (0.92, 1.0), (1.0, 0.1)]
SPIKE_NECK = 0.3                # the share of its length that is the dark neck
EMITTER = (24.5, 46.2, 2.15, 2.6)


def materials():
    pal = k.level_palette()

    def mat(name, index, metallic, roughness, glow=None):
        if glow:
            return k.material(name, palette=index, metallic=metallic, roughness=roughness, emission=pal[index],
                              emission_strength=glow)
        return k.material(name, palette=index, metallic=metallic, roughness=roughness)
    return {
        "body": mat("bgate_body", 0x38, 0.2, 0.3, 0.12),
        "side": mat("bgate_side", 0x35, 0.2, 0.35, 0.08),
        "groove": mat("bgate_groove", 0x32, 0.15, 0.45),
        "lit": mat("bgate_lit", 0x3a, 0.2, 0.28, 0.14),
        "ridge": mat("bgate_ridge", 0x3c, 0.2, 0.25, 0.2),
        "spike": mat("bgate_spike", 0x39, 0.2, 0.25, 0.16),
        "crease": mat("bgate_crease", 0x31, 0.15, 0.45),
        "grey": mat("bgate_grey", 0x6a, 0.45, 0.32),
        "grey_side": mat("bgate_grey_side", 0x07, 0.45, 0.36),
        "grey_dark": mat("bgate_grey_dark", 0x04, 0.4, 0.45),
        "black": mat("bgate_black", 0x02, 0.2, 0.55),
        "core": mat("bgate_core", 0x0a, 0.0, 0.2, 0.6),
    }


# --- Fields -----------------------------------------------------------------------------------------------------------

def seg_distance(x, y, line):
    best = 1e9
    for (ax, ay), (bx, by) in zip(line, line[1:]):
        dx, dy = bx - ax, by - ay
        t = max(0.0, min(1.0, ((x - ax) * dx + (y - ay) * dy) / max(dx * dx + dy * dy, 1e-12)))
        best = min(best, math.hypot(x - ax - t * dx, y - ay - t * dy))
    return best


def centres(points):
    """Pixel centres (column, row) as model coordinates."""
    return [(c + 0.5 - 24.0, 27.5 - r) for c, r in points]


def both(points):
    """A polyline and its mirror image (model coordinates)."""
    pts = centres(points)
    return [pts, [(MX(x), y) for x, y in pts]]


GROOVE_LINES = [(line, depth, w) for pts, depth, w in GROOVES for line in both(pts)]
RIDGE_LINES = [(line, up, w) for pts, up, w in RIDGES for line in both(pts)]
STRUT_LINES = both(STRUT)


def bumps(x, y):
    total = 0.0
    for (c, r), (rx, ry), h in BUMPS:
        cx, cy = c + 0.5 - 24.0, 27.5 - r
        for bx in (cx, MX(cx)):
            q = ((x - bx) / rx) ** 2 + ((y - cy) / ry) ** 2
            if q < 4.0:
                total += h * math.exp(-1.6 * q)
    (c, r), (rx, ry), h = HORN
    cx, cy = c + 0.5 - 24.0, 27.5 - r
    for bx in (cx, MX(cx)):
        u, v = (x - bx) / rx, (y - cy) / ry
        q = u * u + v * v
        if q < 1.0:
            total += h * (1.0 - q) ** 0.55
    return total


def groove_field(x, y):
    """0..1: how much a point lies in a groove (or the strut's channel)."""
    g = 0.0
    for line, depth, w in GROOVE_LINES:
        g = max(g, math.exp(-(seg_distance(x, y, line) / w) ** 2))
    return g


def ridge_field(x, y):
    r = 0.0
    for line, up, w in RIDGE_LINES:
        r = max(r, math.exp(-(seg_distance(x, y, line) / w) ** 2))
    return r


def lip_field(x, y):
    (c, r), (rx, ry) = LIP
    cx, cy = c - 24.0, 28.0 - r
    return math.exp(-(((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2) ** 2)


def blob_field(x, y):
    (c, r), (rx, ry), h = BUMPS[-1]
    cx, cy = c + 0.5 - 24.0, 27.5 - r
    return max(math.exp(-(((x - bx) / rx) ** 2 + ((y - cy) / ry) ** 2)) for bx in (cx, MX(cx)))


def channel(x, y):
    return min(seg_distance(x, y, line) for line in STRUT_LINES)


def body_height(x, y, d):
    """The body's top: the low wall along the outline rising as a quarter circle, the horns, bumps, ridges, grooves
    and the strut's channel."""
    top = BODY_Z + bumps(x, y)
    for line, up, w in RIDGE_LINES:
        top += up * math.exp(-(seg_distance(x, y, line) / w) ** 2)
    for line, depth, w in GROOVE_LINES:
        top -= depth * math.exp(-(seg_distance(x, y, line) / w) ** 2)
    c = channel(x, y)
    top -= CHANNEL_D * math.exp(-(c / CHANNEL_W) ** 4)
    top = max(top, EDGE_Z + 0.5)
    return EDGE_Z + (top - EDGE_Z) * round_edge(d, EDGE_R)


def body_outline():
    left = [P(c, r) for c, r in OUTLINE_LEFT]
    right = [(MX(x), y) for x, y in reversed(left[1:-1])]
    return ccw(chaikin(left + right, 1))


REGION = Region([body_outline()])
_light = {}


def light(x, y):
    """How the body's top at (x, y) faces the sun (n . LIGHT, from the height's slopes), for painting it as the sprite
    paints it: lit along the sides turned to the upper left, shaded on the others."""
    key = (round(x, 3), round(y, 3))
    if key not in _light:
        h = 0.3
        pts = [(x - h, y), (x + h, y), (x, y - h), (x, y + h)]
        inside = REGION.inside(pts)
        dist = REGION.distance(pts)
        z = [body_height(px, py, float(dd)) if ok else EDGE_Z for (px, py), ok, dd in zip(pts, inside, dist)]
        n = Vector((-(z[1] - z[0]) / (2 * h), -(z[3] - z[2]) / (2 * h), 1.0)).normalized()
        _light[key] = n.dot(LIGHT)
    return _light[key]


def body_paint(x, y, d):
    if d < RIM_W:
        return "side"
    if groove_field(x, y) > 0.5 or channel(x, y) < CHANNEL_W:
        return "groove"
    if lip_field(x, y) > 0.5 or blob_field(x, y) > 0.5 or ridge_field(x, y) > 0.5:
        return "ridge"
    lit = light(x, y)
    if lit > LIT_MIN:
        return "lit"
    if lit < SHADE_MAX:
        return "side"
    return "body"


def inward_rings(poly, offsets, spacing):
    """Points d inside the outline for each d of offsets (the outline's points moved along its inward normals)."""
    ring = resample(poly, spacing)
    n = len(ring)
    out = []
    for d in offsets:
        for i, (x, y) in enumerate(ring):
            (ax, ay), (bx, by) = ring[i - 1], ring[(i + 1) % n]
            tx, ty = bx - ax, by - ay
            length = math.hypot(tx, ty) or 1.0
            out.append((x - ty / length * d, y + tx / length * d, d))   # left of a counter-clockwise outline: inside
    return out


def feature_relief(name, poly, height, mats, paint, borders, side="side", bottom=0.0):
    """polish_ring_machine.relief() over one outline, its top triangulated over rows of points laid along the outline
    (rings inside it), along the grooves, ridges and the strut's channel (offset curves either side) and a coarser
    lattice between (polish_fire_gate's housing): the features come out smooth, the flat parts cheap."""
    region = Region([poly])
    outline = resample(poly, 0.38)
    pool = Thinned(0.16)
    for p in outline:
        pool.add(p, 0.05)
    lines = [(line, w) for line, _, w in GROOVE_LINES] + [(line, w) for line, _, w in RIDGE_LINES]
    lines += [(line, CHANNEL_W * 0.7) for line in STRUT_LINES]
    candidates = []
    for line, w in lines:
        for o in (0.0, 0.5, -0.5, 1.15, -1.15, 2.0, -2.0):
            candidates += [(p, 0.24) for p in open_resample(offset_curve(line, o * w), 0.44)]
    for x, y, d in inward_rings(poly, (0.32, 0.85, 1.6, 2.5), 0.46):
        candidates.append(((x, y), 0.3))
    j = 0
    step = 0.9
    y = -27.0
    while y <= 28.5:
        x = -21.0 + (step / 2 if j % 2 else 0.0)
        while x <= 22.0:
            candidates.append(((x, y), 0.4))
            x += step
        y += step * math.sqrt(3) / 2
        j += 1
    pts = [p for p, _ in candidates]
    inside = region.inside(pts)
    dist = region.distance(pts)
    for (p, gap), ok, dd in zip(candidates, inside, dist):
        if ok and dd > 0.26:
            pool.add(p, gap)
    points = pool.points
    n = len(outline)
    edges = [(i, (i + 1) % n) for i in range(n)]
    verts, _e, faces, *_ = geometry.delaunay_2d_cdt([Vector(p) for p in points], edges, [], 0, 1e-6)
    tris = [f for f in faces if len(f) == 3]
    cents = [(sum(verts[i].x for i in f) / 3, sum(verts[i].y for i in f) / 3) for f in tris]
    tris = [f for f, ok in zip(tris, region.inside(cents)) if ok]
    bm = bmesh.new()
    top = [bm.verts.new((v.x, v.y, 0.0)) for v in verts]
    for f in tris:
        try:
            bm.faces.new([top[i] for i in f])
        except ValueError:
            pass
    for v in [v for v in bm.verts if not v.link_faces]:
        bm.verts.remove(v)
    dcache = {}

    def dist_of(v):
        if v not in dcache:
            dcache[v] = float(region.distance([(v.co.x, v.co.y)])[0])
        return dcache[v]
    on_outline = set(v for v in bm.verts if dist_of(v) < 1e-4)
    for field, threshold in borders:
        values = {v: field(v.co.x, v.co.y, dist_of(v)) for v in bm.verts}
        made = split_along(bm, values, threshold)
        for v in made:
            if any(len(e.link_faces) == 1 for e in v.link_edges):
                on_outline.add(v)
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    keys = []
    for f in bm.faces:
        c = f.calc_center_median()
        d = sum(0.0 if v in on_outline else dist_of(v) for v in f.verts) / len(f.verts)
        keys.append(paint(c.x, c.y, d))
    top_faces = list(bm.faces)
    for v in bm.verts:
        v.co.z = height(v.co.x, v.co.y, 0.0 if v in on_outline else dist_of(v))
    # The low wall along the outline down to the base, and the flat underside.
    rim = [e for e in bm.edges if len(e.link_faces) == 1]
    lower = {}
    for e in rim:
        for v in e.verts:
            if v not in lower:
                lower[v] = bm.verts.new((v.co.x, v.co.y, bottom))
    for e in rim:
        a_, b_ = e.verts
        bm.faces.new([b_, a_, lower[a_], lower[b_]])
    loop = list(lower.keys())
    index = {v: i for i, v in enumerate(loop)}
    under, _e2, under_faces, under_orig, *_ = geometry.delaunay_2d_cdt(
        [Vector((v.co.x, v.co.y)) for v in loop], [(index[e.verts[0]], index[e.verts[1]]) for e in rim], [], 0, 1e-6)
    to_lower = {i: lower[loop[o[0]]] for i, o in enumerate(under_orig) if o}
    under_tris = [f for f in under_faces if len(f) == 3 and all(i in to_lower for i in f)]
    cents = [(sum(under[i].x for i in f) / 3, sum(under[i].y for i in f) / 3) for f in under_tris]
    for f, ok in zip(under_tris, region.inside(cents) if under_tris else []):
        if ok:
            try:
                bm.faces.new([to_lower[i] for i in reversed(f)])
            except ValueError:
                pass
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    face_keys = {f: key for f, key in zip(top_faces, keys)}
    mesh = bpy.data.meshes.new(name)
    names = []
    for f in bm.faces:
        key = face_keys.get(f, side)
        if key not in names:
            names.append(key)
    for key in names:
        mesh.materials.append(mats[key])
    for f in bm.faces:
        f.material_index = names.index(face_keys.get(f, side))
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    return k.smooth(obj, 60.0)


def body(m):
    borders = [(lambda x, y, d: d, RIM_W), (lambda x, y, d: groove_field(x, y), 0.5),
               (lambda x, y, d: channel(x, y), CHANNEL_W), (lambda x, y, d: ridge_field(x, y), 0.5),
               (lambda x, y, d: max(lip_field(x, y), blob_field(x, y)), 0.5),
               (lambda x, y, d: light(x, y), LIT_MIN), (lambda x, y, d: light(x, y), SHADE_MAX)]
    return feature_relief("body", body_outline(), body_height, m, body_paint, borders)


# --- The machined parts (the left half's) -----------------------------------------------------------------------------

def paint_grey(obj, m, keep=()):
    names = {m[n].name for n in keep}
    mats = obj.data.materials

    def pick(c, n):
        if n.z > 0.8:
            return m["grey"]
        if n.z < -0.3:
            return m["black"]
        if n.dot(LIGHT) > 0.45:
            return m["grey_side"]
        return m["grey_dark"]
    slots = {}
    for poly in obj.data.polygons:
        cur = mats[poly.material_index]
        if cur is not None and cur.name in names:
            continue
        mat = pick(poly.center, poly.normal)
        if mat.name not in slots:
            slots[mat.name] = mk.slot_of(obj, mat)
        poly.material_index = slots[mat.name]
    return obj


def bracket(m):
    c0, c1, r0, r1 = BRACKET
    w0, w1, v0, v1 = BRACKET_WINDOW
    z0, z1 = BRACKET_Z
    frame = mk.box("bracket", XE(c0), XE(c1), YE(r1), YE(r0), z0, z1, m["grey"])
    mk.bevel(frame, 0.32, 2, 35.0)
    window = mk.box("bracket_window", XE(w0), XE(w1), YE(v1), YE(v0), -5.0, 20.0, m["black"])
    mk.boolean(frame, window, "DIFFERENCE")
    mk.cleanup(frame, dissolve=0.0)
    paint_grey(frame, m, keep=("black",))
    return mk.shade(frame, 35.0)


def strut(m, hit):
    line = mk.chaikin([(c + 0.5 - 24.0, 27.5 - r) for c, r in STRUT], 2, closed=False)
    pts, ups = [], []
    dense = []                          # about every 0.4
    for (ax, ay), (bx, by) in zip(line, line[1:]):
        n = max(1, int(math.hypot(bx - ax, by - ay) / 0.4))
        for i in range(n):
            dense.append((ax + (bx - ax) * i / n, ay + (by - ay) * i / n))
    dense.append(line[-1])
    for x, y in dense:
        h = hit(x, y)
        pts.append(Vector((x, y, (h[0].z if h else BODY_Z) - 0.2)))
        ups.append(h[1] if h else Vector((0, 0, 1)))
    bar = mk.bar("strut", pts, ups, STRUT_W, STRUT_UP + 0.2, 0.9, m["grey"], 14, 4.0)
    paint_grey(bar, m)
    return k.smooth(bar, 40)


def collar(m):
    c0, c1, r0, r1, top = COLLAR
    block = mk.box("collar", XE(c0), XE(c1), YE(r1), YE(r0), 0.2, top, m["grey"])
    mk.bevel(block, 0.55, 3, 35.0)
    paint_grey(block, m)
    return mk.shade(block, 35.0)


# --- The spike and the emitter (whole) --------------------------------------------------------------------------------

def spike(m):
    """A bud turned about an axis from its foot (on the emitter) to its tip, leaning back up the screen: its section two
    lobes with a crease between them along its top; the neck dark."""
    fc, fr, fz = SPIKE_FOOT
    tc, tr, tz = SPIKE_TIP
    foot = Vector((XE(fc), YE(fr), fz))
    tip = Vector((XE(tc), YE(tr), tz))
    axis = tip - foot
    length = axis.length
    w = axis.normalized()
    u = Vector((1.0, 0.0, 0.0))
    v = w.cross(u).normalized()          # across the axis, upwards (towards the camera)
    segments = 28
    rings = []
    samples = 30
    prof = SPIKE_PROFILE
    for i in range(samples + 1):
        t = i / samples
        for j in range(len(prof) - 1):
            if prof[j][0] <= t <= prof[j + 1][0]:
                f = (t - prof[j][0]) / (prof[j + 1][0] - prof[j][0])
                f = f * f * (3 - 2 * f)
                r = prof[j][1] + (prof[j + 1][1] - prof[j][1]) * f
                break
        ring = []
        for s in range(segments):
            a = 2 * math.pi * s / segments
            # the crease along the top (a = pi/2: towards v)
            dip = 0.4 * math.exp(-((math.atan2(math.sin(a - math.pi / 2), math.cos(a - math.pi / 2))) / 0.45) ** 2)
            rr = r * (1.0 - dip * min(1.0, t / SPIKE_NECK))
            ring.append(foot + w * (t * length) + (u * math.cos(a) * 1.0 + v * math.sin(a) * 0.82) * rr)
        rings.append(ring)
    bud = k.loft("spike", rings, m["spike"], start_point=foot - w * 0.1, end_point=tip)
    values = []
    for vert in bud.data.vertices:
        rel = vert.co - foot
        t = rel.dot(w) / length
        side = rel - w * rel.dot(w)
        a = math.atan2(side.dot(v), side.dot(u))
        crease = math.exp(-((math.atan2(math.sin(a - math.pi / 2), math.cos(a - math.pi / 2))) / 0.42) ** 2)
        neck = 1.0 if t < SPIKE_NECK else 0.0
        values.append(max(crease if t > 0.25 else 0.0, neck))
    band_split(bud, values, [(-9.0, m["spike"]), (0.55, m["crease"])])
    return k.smooth(bud, 60)


def emitter(m):
    c, r, rad, h = EMITTER
    x, y = XE(c), YE(r)
    cup = mk.lathe("emitter", [(rad, 0.4), (rad + 0.15, h - 0.6), (rad - 0.1, h), (rad - 0.6, h + 0.05),
                               (rad - 0.75, h - 0.35), (0.01, h - 0.55)], (x, y), m["grey_dark"], 32)
    k.smooth(cup, 45)
    mk.paint(cup, lambda c_, n: m["grey"] if n.z > 0.6 and c_.z > h - 0.1 else None)
    core = mk.dome("emitter_core", (x - 0.2, y - 0.1), (rad - 0.65, rad - 0.75, 0.95), h - 0.55, m["core"], 24, 6)
    return [cup, core]


def mirror_about_axis(objects):
    """Copies of objects mirrored about x = AX, keeping their shading (polish_ice_globe.py's)."""
    flip = Matrix.Translation((AX, 0, 0)) @ Matrix.Scale(-1, 4, (1, 0, 0)) @ Matrix.Translation((-AX, 0, 0))
    out = []
    for obj in objects:
        mk.apply(obj)
        copy = obj.copy()
        copy.data = obj.data.copy()
        copy.name = obj.name + "_r"
        bpy.context.scene.collection.objects.link(copy)
        mesh = copy.data
        corner = {}
        for poly in mesh.polygons:
            for li in poly.loop_indices:
                n = mesh.corner_normals[li].vector
                corner[(poly.index, mesh.loops[li].vertex_index)] = (-n.x, n.y, n.z)
        mesh.transform(flip)
        mesh.flip_normals()
        normals = [None] * len(mesh.loops)
        for poly in mesh.polygons:
            for li in poly.loop_indices:
                normals[li] = corner[(poly.index, mesh.loops[li].vertex_index)]
        mesh.normals_split_custom_set(normals)
        out.append(copy)
    return out


def build_whole():
    m = materials()
    main = body(m)
    bpy.context.view_layer.update()
    hit = mk.surface([main])
    left = [bracket(m), strut(m, hit), collar(m)]
    mirror_about_axis(left)
    spike(m)
    emitter(m)
    whole = [o for o in mk.meshes() if len(o.data.polygons) > 0]
    for obj in whole:
        mk.apply(obj)
    triangulate(whole)
    bpy.context.view_layer.update()
    return whole, m


# --- Checks, previews, export -----------------------------------------------------------------------------------------

def whole_mask(sheet):
    mask = [[False] * 48 for _ in range(56)]
    for sprite, (c0, r0) in SPRITE_CELLS.items():
        part = k.sprite_mask(sheet, sprite)
        for r in range(28):
            for c in range(24):
                if part[r][c]:
                    mask[r0 + r][c0 + c] = True
    return mask


def build():
    k.reset()
    options = k.args()
    out = mk.outdir(options)
    only = options["only"].split(",") if "only" in options else None
    whole, m = build_whole()
    low, high = mk.bounds(whole)
    print("== whole gate: %d triangles, %d objects, %d materials, x %.2f..%.2f y %.2f..%.2f z %.2f..%.2f" % (
        mk.triangles(whole), len(whole), len(mk.materials_of(whole)), low.x, high.x, low.y, high.y, low.z, high.z))
    if options.get("stats") == "1":
        for obj in sorted(whole, key=lambda o: -mk.triangles([o]))[:16]:
            print("   %-22s %6d" % (obj.name, mk.triangles([obj])))
    sheet = None
    if "check" in options:
        sheets = options["check"]
        sheet = os.path.join(sheets, "enemy_x5e.png") if os.path.isdir(sheets) else sheets
        mk.compare("whole (^ 16 18 above 54 56)", mk.coverage(whole, 48, 56), whole_mask(sheet))
    bpy.context.scene.view_settings.view_transform = "Standard"
    if "preview" in options:
        mk.preview(options["preview"] + "blue_gate_whole", whole, size=(48, 56), scale=10, distance=1.9)
    if "whole" in options:
        mk.export(whole, options["whole"])
    if only == ["none"]:
        return
    for name, sprite, box in PIECES:
        if only and name not in only:
            continue
        parts = [p for p in (cut(src, box, m["black"]) for src in whole) if p is not None]
        db.drop_unused(parts)
        mk.transform(parts, Matrix.Translation((-(box[0] + box[1]) / 2, -(box[2] + box[3]) / 2, 0)))
        bpy.context.view_layer.update()
        triangulate(parts)
        parts = [db.join(parts, name)]
        parts[0].data.name = name
        for src in whole:
            src.hide_render = True
        if sheet:
            mk.compare("%s (^ %d)" % (name, sprite), mk.coverage(parts, 24, 28), k.sprite_mask(sheet, sprite))
        mk.report(name, parts, os.path.join(out, name + ".glb"))
        if "preview" in options and options.get("pieces") == "1":
            mk.preview(options["preview"] + name, parts)
        for obj in parts:
            data = obj.data
            bpy.data.objects.remove(obj)
            if data.users == 0:
                bpy.data.meshes.remove(data)
        for src in whole:
            src.hide_render = False


if __name__ == "__main__":
    build()
