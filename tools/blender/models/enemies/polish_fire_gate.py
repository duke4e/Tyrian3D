"""The fire gates of APPROACH, MISTAKES and SOH JIN (sheet A, written a in models.cfg; 2x2 sprites, 24 x 28 pixels):
a steel housing at each edge of the screen with a flap of fire hinged to its flat side, polished (2026-10-20; it
replaces wave3_q.py's housing_whole(), a heightfield half dome painted in the sprite's shades, wave2_h.py's
fire_flap(), a plain slab painted in bands of the flap's pixels and glowing up to 2.5, and wave3_ar_flap.py, which
swung wave2_h's flap for the frame lines). models.cfg: model fire_housing_l_top / _l_bottom / _r_top / _r_bottom,
fire_flap_r_top / _r_bottom / _l_top / _l_bottom and the frame models fire_flap_235 ... fire_flap_39 (all origin);
sprite a 229 fire_housing_l_top yaw=0 height=-4 and so on; frame a 235 fire_flap_235 and so on.

The levels build each gate from eight enemies (episode 2's 780-787 in SOH JIN and MISTAKES, episode 4's 802-809 in
APPROACH; ground and ground2 slots, moving down with the map): at the screen's left edge the housing A 229 above 267
at x 25 with its flap A 237 above 275 24 pixels to its right, at the right edge the mirror image, the flap A 7 above
45 at x 240 and the housing A 9 above 47 at x 264; each top sprite 28 pixels above its bottom one. 9, 47, 7 and 45
are 229, 267, 237 and 275 flipped left to right, pixel for pixel and index for index (and so are the flaps' other
frames, 5 43, 3 41, 1 39 of 235 273, 233 271, 231 269): the left gate is built and mirrored. The housings have
armour (100); the flaps can't be hit (armour 0) and don't animate by themselves: they show their first frame, the
flap standing on edge on its hinge, until a level event (24, global animate, once: APPROACH's links 165 and 185, SOH
JIN's 45, 165 and 185, MISTAKES' 25, 45 and 165) plays their 19 frames once, 237 237 237 235 235 235 233 233 233 231
231 231 233 233 233 235 235 235 237 and the same for the other pieces: the flap swinging down flat and up again.
No other enemy shows these sprites. So each flap piece has a model for its first frame and frame models for the
three others: the flap swung up 66 degrees (235 273, mirrored 5 43), 46 degrees (233 271, 3 41) and lying flat, its
fire up (231 269, 1 39), the angles where its fire face reaches as far from the hinge as the frames draw it (5 and
8 pixels; 11 lying flat).

As the sprites and their 4x upscales draw the left gate (the 48 x 56 picture: the housing's columns 0-23, the flap's
24-47; rows 0-27 the top sprites', 28-55 the bottom ones'): the housing a half dome (columns 1-22 of rows 6-49), its
flat side to the right, like a steel fish's head: a dark glossy eye in a socket near its top (columns 9-13 of rows
10-17, its glint at column 12, row 14) under a small rivet (column 12, row 9); along the flat side a pillar of two
bright ribs (columns 15-17 from the top to row 20, 19-20 from the top to row 45) and the lit edge (column 22); where
the inner rib ends, a bracket forking down (columns 13 and 15 of rows 20-24) over a round knob (rows 25-29); a crease
running from the brow down the cheek and round under it to the pillar (rows 16-36), the jaw's lit ridge sweeping round
below it (rows 38-44), the cheek between them darker. The hinge (the housing's column 23 and the flap's 0-1): three
grey steel knuckles (rows 10-14, 24-30, 40-44) and between them the flap's red edge. The flap standing on edge is that
red line; swinging down it shows its fire face: lying flat (231 over 269) a plate of fire 11 pixels across from the
hinge (rows 9-46), a dark red rim round yellow and white-hot flames (a blob at the top, a bar across row 19, a big
swirl in the lower half).

The housing: the shell is a solid over its plan (an ellipse cut by the flat side, the corners rounded), its top a
dome with the eye's socket and brow, the crease, the jaw's ridge, a groove under it (the gill), a lip along the flat
side and its edge rounded off, triangulated over rows of points laid along those features (so they and the colour
borders come out smooth) and painted face by face in the steel ramp's shades (ramp 6); straight walls down to a
skirt below the ground. The ribs and the bracket's prongs are bars laid on the shell, lit along their tops; the knob
is turned, the eye a glossy dark lens set along the shell's normal with a small glowing glint.

The flap: a plate of fire in a frame of round red-hot rods, the hinge rod on the axis, built lying flat (its fire
face up) and swung up about the hinge's axis for each frame; its heat is the open frame's pixels (and the hinge column
beside them), Gaussian-smoothed, with flame streaks running across it, the rods no hotter than red (as the standing
frame draws its edge), the back face three shades cooler (the side the game's camera sees when the flap stands at the
screen's edge); the hot flames swell out of the fire face. The heat is cut into bands of the fire ramp's palette
indices (smooth contours, polish_orb_red.band_split), each glowing in its own colour, well under 1 (the game's bloom
burnt the fire wall white at 2.2). The three steel knuckles stay put as the flap swings; they are the flap's (the
flap can't be destroyed, the housing can), reaching half a pixel into the housing's flat side.

The pieces: the housing and the flap are separate objects (separate enemies, side by side); each is built whole over
both its sprites and cut along their edge (y = 0; polish_arch.cut: the pieces keep the whole's shading across the
cut), each piece moved so that its sprite's centre is its origin. Frame models: the same flap swung, cut the same way.

Where they stand: models drawn at their origin stand at the ground enemies' layer, about 4 pixels above the terrain;
"height=-4" on the sprite lines sets the gates on the ground (the housings' skirt reaches 1.5 below z = 0).

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up from the ground (z = 0); the left
gate's origin is the edge between the housing and the flap at the middle of their height: column c of the picture
starts at x = c - 24, row r at y = 28 - r. The housing's top sprite's centre is (-12, 14), the flap's (12, 14).

Replaces, so that they don't overwrite these models: wave3_ar_flap.py (delete it: it built only the frame models,
from wave2_h's flap; wave3_ar_kit.py stays, its docstring's mention of it goes); in wave2_h.py the fire flap's
section (FLAP_FACE, FLAP_TOP, FLAP_BOTTOM, FLAP_HINGE_X, FLAP_HINGE_Z, FLAP_KNUCKLES, _flap_field(), fire_flap() and
fire_flap_r_top() ... fire_flap_l_bottom()), its four MODELS entries, the flaps' paragraph of its docstring, and
Matrix and round_edge from its imports (only the flap used them); in wave3_q.py steel_mats(), paint_shell() and the
housings' section (HOUSING_ORIGIN, HOUSING_FLAT, HOUSING_EYE, housing_whole() with its @q.whole("housing", ...)
registration, HOUSING_PIECES, housing_piece() and the loop registering fire_housing_*), the housings' paragraph of
its docstring, "housing|" from its --whole usage and its math import; wave3_q_art.py's HOUSING and FLAP_OPEN (nothing
else reads them). wave3_q_kit.py's HalfDome, ellipse_dent, clamp_poly and rib are then unused (only the housings
called them).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouettes of each
whole gate and each piece against enemy_A.png), --preview <prefix> (each gate's top and 3/4 views, frame by frame;
--pieces 1 also each piece's), --only <name,...>, --sides left,right (which gates), --stats 1 (the housing's
triangles part by part).
"""
import math
import os
import sys

import bmesh
import bpy
import mathutils.noise as noise
from mathutils import Matrix, Vector, geometry

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k, smoothstep  # noqa: E402
from polish_arch import cut  # noqa: E402  (polish_machine_kit.cut without its material indices shifted twice)
from polish_orb_red import band_split  # noqa: E402
from polish_ring_machine import ccw, resample  # noqa: E402


def YE(r):
    """The top edge of the picture's row r (the top sprites' rows 0-27, the bottom ones' 28-55)."""
    return 28.0 - r


# --- The pieces ----------------------------------------------------------------------------------------------------
# The housings: (model, sprite, the sprite's centre in the whole) for the left gate and its mirror image.
HOUSINGS = {"left": [("fire_housing_l_top", 229, (-12.0, 14.0)), ("fire_housing_l_bottom", 267, (-12.0, -14.0))],
            "right": [("fire_housing_r_top", 9, (12.0, 14.0)), ("fire_housing_r_bottom", 47, (12.0, -14.0))]}
# The flap's frames: degrees up from lying flat, then (model, sprite) of the left gate's flap (top, bottom) and of the
# right gate's (top, bottom). The first frame, standing on edge, is the enemies' sprite; the others are frame models.
SWING_65, SWING_45 = 66.0, 46.0
FRAMES = [(90.0, [("fire_flap_r_top", 237), ("fire_flap_r_bottom", 275)], [("fire_flap_l_top", 7), ("fire_flap_l_bottom", 45)]),
          (SWING_65, [("fire_flap_235", 235), ("fire_flap_273", 273)], [("fire_flap_5", 5), ("fire_flap_43", 43)]),
          (SWING_45, [("fire_flap_233", 233), ("fire_flap_271", 271)], [("fire_flap_3", 3), ("fire_flap_41", 41)]),
          (0.0, [("fire_flap_231", 231), ("fire_flap_269", 269)], [("fire_flap_1", 1), ("fire_flap_39", 39)])]
FLAP_CENTRES = {"left": [(12.0, 14.0), (12.0, -14.0)], "right": [(-12.0, 14.0), (-12.0, -14.0)]}

# --- Shared geometry helpers -----------------------------------------------------------------------------------------

def open_resample(points, spacing):
    """An open polyline resampled to points about `spacing` apart (its ends kept)."""
    lengths = [math.dist(a, b) for a, b in zip(points, points[1:])]
    total = sum(lengths)
    count = max(2, int(round(total / spacing)) + 1)
    out, i, walked = [], 0, 0.0
    for c in range(count):
        target = total * c / (count - 1)
        while i < len(lengths) - 1 and walked + lengths[i] < target:
            walked += lengths[i]
            i += 1
        t = (target - walked) / lengths[i] if lengths[i] > 0 else 0.0
        (x0, y0), (x1, y1) = points[i], points[i + 1]
        out.append((x0 + (x1 - x0) * min(t, 1.0), y0 + (y1 - y0) * min(t, 1.0)))
    return out


def offset_curve(points, offset):
    """An open polyline moved sideways (to the left of its direction for a positive offset)."""
    out = []
    n = len(points)
    for i, (x, y) in enumerate(points):
        ax, ay = points[max(i - 1, 0)]
        bx, by = points[min(i + 1, n - 1)]
        tx, ty = bx - ax, by - ay
        length = math.hypot(tx, ty) or 1.0
        out.append((x - ty / length * offset, y + tx / length * offset))
    return out


def polyline_distance(points):
    """distance(x, y) to an open polyline."""
    segs = list(zip(points, points[1:]))

    def dist(x, y):
        best = 1e9
        for (ax, ay), (bx, by) in segs:
            dx, dy = bx - ax, by - ay
            t = max(0.0, min(1.0, ((x - ax) * dx + (y - ay) * dy) / max(dx * dx + dy * dy, 1e-12)))
            best = min(best, math.hypot(x - ax - t * dx, y - ay - t * dy))
        return best
    return dist


class Thinned:
    """A point set that refuses points closer than `gap` to one it holds (a grid of buckets)."""

    def __init__(self, gap):
        self.gap = gap
        self.cells = {}
        self.points = []

    def add(self, p, gap=None):
        g = self.gap if gap is None else gap
        cx, cy = int(math.floor(p[0] / self.gap)), int(math.floor(p[1] / self.gap))
        reach = int(math.ceil(g / self.gap))
        for i in range(cx - reach, cx + reach + 1):
            for j in range(cy - reach, cy + reach + 1):
                for q in self.cells.get((i, j), ()):
                    if (q[0] - p[0]) ** 2 + (q[1] - p[1]) ** 2 < g * g:
                        return False
        self.cells.setdefault((cx, cy), []).append(p)
        self.points.append(p)
        return True


def lattice(x0, x1, y0, y1, step):
    """A triangular lattice of points over a box."""
    out = []
    j = 0
    y = y0
    while y <= y1:
        x = x0 + (step / 2 if j % 2 else 0.0)
        while x <= x1:
            out.append((x, y))
            x += step
        y += step * math.sqrt(3) / 2
        j += 1
    return out


# --- The flap ------------------------------------------------------------------------------------------------------
XH, ZH = 0.2, 1.75          # the hinge's axis (along y): x, height
FLAP_L = 10.8               # from the axis to the far edge (x 11 lying flat: the open frame's column 10)
FLAP_Y = (-19.0, 19.0)      # its bottom and top edges (rows 46 and 9)
ROD = 0.95                  # the frame's round rods (radius); the hinge rod lies on the axis
CORNER = 1.6                # the frame's corners, rounded in plan
PLATE = 0.46                # half the plate's thickness inside the frame
BULGE = 0.75                # how far the hottest flames swell out of the fire face
BACK_COOL = 3.0             # the back face's fire, this many shades cooler
RIM_HEAT = 7.5              # the rods glow no hotter than this (red-hot iron round the fire)
KNUCKLES = [(YE(15), YE(10)), (YE(31), YE(24)), (YE(45), YE(40))]   # the hinge's steel knuckles (rows 10-14, 24-30,
KNUCKLE_R = 1.65                                                    # 40-44)

# The open flap's fire (A 231 over 269, rows 9-46, columns 0-10; shades of the fire ramp 7, 0-f; g: the knuckles'
# steel, filled in from the fire beside them), and the hinge's column beside it (the housing's column 23).
FACE = """
4444444441.
gg455556541
gg666667763
gg888aba964
ggabcffca95
ggbddffdaa6
69abcdda9b7
6aa999a8ac9
9abaaaaacda
bccccccceeb
ddddeeefffb
bccccccceeb
aaaabcccddb
88888abbcda
7777778abca
gg777779aba
gg688879aba
gg6888889a9
gg5999999a9
gg7aaaaa9a9
gg9ccccbab9
gg9ddddcbc7
46aeeffdcd7
57adeeeecd6
59befffedf6
5abdfffedf6
49abdddddf5
479abccdde5
3678999bdd4
3456789abc4
334679aaac4
gg78aaa9ab4
ggb799988b3
gg634558ac2
gg344568c91
gg49999b930
355555542..
23222221000
"""
HINGE_COLUMN = "4ggggg447899985gggg" + "ggg455542323ggggg32"
FACE_TOP_ROW = 9

# The heat bands: (lowest heat, palette index, emission strength in the palette colour), heat as the sprites' shades
# of the fire ramp (0-15). Kept well under 1: the game's bloom brightens them (the fire wall burned white at 2.2).
BANDS = [(-99.0, 0x72, 0.1), (3.5, 0x74, 0.14), (5.0, 0x75, 0.17), (6.0, 0x76, 0.2), (7.0, 0x77, 0.24),
         (8.0, 0x78, 0.28), (9.0, 0x79, 0.32), (10.0, 0x7a, 0.36), (11.0, 0x7b, 0.4), (12.0, 0x7c, 0.45),
         (13.0, 0x7d, 0.5), (14.0, 0x7e, 0.56), (14.8, 0x7f, 0.62)]
CAP = 0x77                  # the flap's cuts (inside the fire)


class Heat:
    """The open flap's fire at a point lying flat (x, y): the sprite's shades, Gaussian-smoothed between the pixel
    centres."""

    def __init__(self, sigma=0.55):
        grid = []
        for i, row in enumerate(FACE.strip().split("\n")):
            cells = [HINGE_COLUMN[i]] + list(row.ljust(11, "."))
            values = [None if ch in "g." else int(ch, 16) for ch in cells]
            filled = []
            for c, v in enumerate(values):
                if v is None:
                    near = min((abs(c2 - c), v2) for c2, v2 in enumerate(values) if v2 is not None)
                    v = max(0.0, near[1] - 1.0)
                filled.append(float(v))
            grid.append(filled)
        self.grid = grid
        self.sigma = sigma
        self.x0 = -1.0                  # the hinge column's left edge
        self.y0 = YE(FACE_TOP_ROW)      # the top row's top edge

    def __call__(self, x, y):
        c = x - self.x0 - 0.5
        r = self.y0 - y - 0.5
        c0, r0 = int(round(c)), int(round(r))
        total = weight = 0.0
        rows, cols = len(self.grid), len(self.grid[0])
        for rr in range(r0 - 2, r0 + 3):
            for cc in range(c0 - 2, c0 + 3):
                wt = math.exp(-((cc - c) ** 2 + (rr - r) ** 2) / (2 * self.sigma ** 2))
                total += self.grid[min(max(rr, 0), rows - 1)][min(max(cc, 0), cols - 1)] * wt
                weight += wt
        return total / weight


def streaks(u, y):
    """Flame streaks across the plate (along u, away from the hinge): about -1 .. 1."""
    a = noise.noise(Vector((u * 0.42, y * 1.1, 3.7)))
    b = noise.noise(Vector((u * 0.95, y * 2.4, 9.1)))
    return 0.75 * a + 0.4 * b


def smax(a, b, r):
    h = max(r - abs(a - b), 0.0) / r
    return max(a, b) + h * h * r * 0.25


def rod_profile(d):
    """The frame's round rods: the plate's half-thickness at distance d inside its outline."""
    t = d - ROD
    return math.sqrt(max(0.0, ROD * ROD - t * t)) if d < 2 * ROD else 0.0


def rounded_rect_points(u0, u1, y0, y1, r, spacing):
    """Points round a rounded rectangle, counter-clockwise, about `spacing` apart."""
    dense = []
    for (cx, cy, a0) in ((u1 - r, y0 + r, -90.0), (u1 - r, y1 - r, 0.0), (u0 + r, y1 - r, 90.0),
                         (u0 + r, y0 + r, 180.0)):
        for i in range(13):
            a = math.radians(a0 + 90.0 * i / 12)
            dense.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return resample(dense, spacing)


def flap_plate(bands, heat, degrees):
    """The flap: a plate of fire in a frame of round rods (the hinge rod on the axis), built lying flat (its fire
    face up) in (u, y, w): u from the axis across, w up from the hinge's plane; swung up `degrees` about the axis."""
    u0, u1 = -ROD, FLAP_L
    y0, y1 = FLAP_Y
    cu, cy, hw, hh = (u0 + u1) / 2, (y0 + y1) / 2, (u1 - u0) / 2, (y1 - y0) / 2

    def inside(u, y):
        return -mk.rounded_rect_distance(u - cu, y - cy, hw, hh, CORNER)

    def rings(spec):
        out = []
        for d, spacing in spec:
            out += rounded_rect_points(u0 + d, u1 - d, y0 + d, y1 - d, max(0.05, CORNER - d), spacing)
        return out

    boundary = rounded_rect_points(u0, u1, y0, y1, CORNER, 0.42)
    n = len(boundary)
    # The fire face: rows along the rods' round profile, a lattice inside; the back face (seen only edge-on or from
    # the side when the flap stands) coarser.
    front_pts = boundary + rings(((0.15, 0.5), (0.45, 0.5), (0.95, 0.55), (1.5, 0.6))) + \
        [p for p in lattice(u0, u1, y0, y1, 0.7) if inside(*p) > 2.0]
    back_pts = boundary + rings(((0.3, 0.7), (0.95, 0.8))) + [p for p in lattice(u0, u1, y0, y1, 1.15) if inside(*p) > 1.7]

    def triangulate(points):
        edges = [(i, (i + 1) % n) for i in range(n)]
        verts, _e, faces, orig, *_ = geometry.delaunay_2d_cdt([Vector(p) for p in points], edges, [], 0, 1e-6)
        tris = [f for f in faces if len(f) == 3 and
                inside(sum(verts[i].x for i in f) / 3, sum(verts[i].y for i in f) / 3) > 0]
        return verts, tris, [min(o) if o else -1 for o in orig]

    def sample(u, y, d, face):
        """The heat and the half-thickness at (u, y), d inside the outline, on the fire face or the back."""
        h = heat(XH + u, y)
        inner = smoothstep(0.4 * ROD, 1.7 * ROD, d)
        h -= max(0.0, h - RIM_HEAT) * (1.0 - smoothstep(0.9 * ROD, 1.8 * ROD, d))   # the rods: red-hot iron
        s = streaks(u, y) * inner
        if face:
            h += 0.8 * s
            plate = PLATE + BULGE * smoothstep(6.0, 15.0, h) ** 1.2 + 0.07 * s
        else:
            h += 0.6 * s - BACK_COOL * inner
            plate = PLATE + 0.5 * BULGE * smoothstep(6.0, 15.0, h) ** 1.2 + 0.05 * s
        if d < 1e-4:
            return h, 0.0
        return h, smax(rod_profile(d), plate * smoothstep(0.35 * ROD, 1.3 * ROD, d), 0.3)

    bm = bmesh.new()
    values = []
    rim = []
    for u, y in boundary:
        h, _w = sample(u, y, 0.0, True)
        rim.append(bm.verts.new((XH + u, y, ZH)))
        values.append(h)
    for points, face in ((front_pts, True), (back_pts, False)):
        verts, tris, orig = triangulate(points)
        made = []
        for v, o in zip(verts, orig):
            if 0 <= o < n:
                made.append(rim[o])
                continue
            d = max(0.0, inside(v.x, v.y))
            h, w = sample(v.x, v.y, d, face)
            made.append(bm.verts.new((XH + v.x, v.y, ZH + (w if face else -w))))
            values.append(h)
        for f in tris:
            try:
                bm.faces.new([made[i] for i in (f if face else tuple(reversed(f)))])
            except ValueError:
                pass
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mesh = bpy.data.meshes.new("flap")
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new("flap", mesh)
    bpy.context.scene.collection.objects.link(obj)
    band_split(obj, values, bands)
    k.smooth(obj, 60)
    if degrees:
        swing = (Matrix.Translation((XH, 0.0, ZH)) @ Matrix.Rotation(math.radians(-degrees), 4, "Y") @
                 Matrix.Translation((-XH, 0.0, -ZH)))
        obj.data.transform(swing)
        obj.data.update()
    return obj


def knuckles(m):
    """The hinge's steel knuckles round the axis, their rounded ends darker."""
    out = []
    r = KNUCKLE_R
    for i, (y0, y1) in enumerate(KNUCKLES):
        prof = [(y0, r * 0.5), (y0 + 0.1, r * 0.78), (y0 + 0.28, r * 0.93), (y0 + 0.5, r), (y1 - 0.5, r),
                (y1 - 0.28, r * 0.93), (y1 - 0.1, r * 0.78), (y1, r * 0.5)]
        obj = k.lathe(f"knuckle{i}", prof, m["knuckle"], 22, axis_x=XH, axis_z=ZH)
        mk.paint(obj, lambda c, n, y0=y0, y1=y1: m["knuckle_dark"] if (c.y < y0 + 0.4 or c.y > y1 - 0.4) else None)
        k.smooth(obj, 50)
        out.append(obj)
    return out


def flap_materials():
    pal = k.level_palette()
    bands = [(lowest, k.material("fire_flap_%02x" % index, palette=index, metallic=0.0, roughness=0.85,
                                 emission=pal[index], emission_strength=glow))
             for lowest, index, glow in BANDS]
    m = {"knuckle": k.material("fire_knuckle", palette=0x0b, metallic=0.6, roughness=0.28),
         "knuckle_dark": k.material("fire_knuckle_dark", palette=0x07, metallic=0.55, roughness=0.35)}
    m["cap"] = next(mat for _, mat in bands if mat.name.endswith("@%d" % CAP))
    return bands, m


def build_flap(degrees, heat):
    bands, m = flap_materials()
    parts = [flap_plate(bands, heat, degrees)] + knuckles(m)
    for obj in parts:
        mk.apply(obj)
    return parts, m


# --- The housing ---------------------------------------------------------------------------------------------------
XC, AX, BY = -5.3, 17.4, 22.0   # the plan's ellipse: its centre's x, half-width and half-height (y 0 its middle)
XF = -1.0                       # the flat side, against the hinge
FLAT_CORNER = 3.0               # the flat side's ends rounded off in plan
PLAN_CENTRE = (-9.0, 0.0)       # the plan's outlines are traced on rays from here
HEIGHT, DOME_P, DOME_Q = 12.3, 2.2, 2.0
SKIRT = 1.5                     # how far its walls reach below the ground (z 0)
EDGE_R = 1.0                    # the flat side's top edge, rounded
LIP = (0.42, 0.62, 0.3)         # the lip along the flat side's edge: height, distance in from the edge, half-width
# The eye: its socket's middle, half-axes and tilt (degrees counter-clockwise: its top leans towards the flat side),
# depth; the brow round it.
EYE = (-12.2, 14.1, 2.45, 3.55, -14.0)
SOCKET_DEPTH, BROW = 1.5, 0.35
RIVET = (-11.4, 18.7)
# The crease from the brow down the cheek and round under it to the pillar; the jaw's ridge round the bottom.
CREASE = [(-19.5, 12.5), (-19.5, 7.0), (-18.5, 3.8), (-16.8, 1.3), (-14.8, -0.9), (-12.6, -3.3), (-10.3, -5.5),
          (-7.7, -7.2), (-5.1, -8.1)]
CREASE_W, CREASE_D = 0.42, 0.6
JAW = [(-19.6, -7.6), (-16.8, -9.8), (-14.0, -11.4), (-11.2, -13.0), (-8.2, -14.5), (-5.2, -15.5)]
JAW_W, JAW_H = 1.35, 0.7
GILL = [(-17.4, -12.7), (-14.6, -14.6), (-11.4, -16.3), (-8.0, -17.6), (-5.3, -18.2)]   # a groove under the jaw
GILL_W, GILL_D = 0.32, 0.38
# The pillar along the flat side: its ribs as paths on the shell, half-width, how far they stand out. The inner rib
# ends a little below the middle of the top sprite in the bracket, two prongs forking down from its foot (the sprite's
# columns 13 and 15 of rows 20-24), a knob held under them.
RIBS = [("rib_inner", [(-7.6, 21.0), (-7.6, 8.6)], 1.35, 0.85),
        ("rib_outer", [(-4.0, 21.1), (-4.0, -17.6)], 0.92, 0.7),
        ("prong_left", [(-8.1, 9.6), (-9.3, 8.1), (-10.2, 6.0), (-10.4, 3.5)], 0.55, 0.7),
        ("prong_right", [(-7.3, 9.6), (-7.9, 8.0), (-8.3, 5.9), (-8.4, 3.5)], 0.55, 0.7)]
KNOB = (-9.4, 1.8, 1.3, 0.95)   # x, y, radius, how far it stands out (rows 25-28 of the top sprite)

CREASE_LINE = mk.chaikin(CREASE, 3, closed=False)
JAW_LINE = mk.chaikin(JAW, 3, closed=False)
GILL_LINE = mk.chaikin(GILL, 3, closed=False)
CREASE_DIST = polyline_distance(CREASE_LINE)
JAW_DIST = polyline_distance(JAW_LINE)
GILL_DIST = polyline_distance(GILL_LINE)


def dome(x, y):
    rho = math.hypot((x - XC) / AX, y / BY)
    if rho >= 1.0:
        return 0.0
    return HEIGHT * (1.0 - rho ** DOME_P) ** (1.0 / DOME_Q)


def eye_coords(x, y):
    ex, ey, rx, ry, tilt = EYE
    a = math.radians(-tilt)
    dx, dy = x - ex, y - ey
    return (dx * math.cos(a) - dy * math.sin(a)) / rx, (dx * math.sin(a) + dy * math.cos(a)) / ry


def eye_e(x, y):
    return math.hypot(*eye_coords(x, y))


def plan_sdf(x, y):
    """Signed distance (about) to the plan: the ellipse cut by the flat side, its corners rounded."""
    rho = math.hypot((x - XC) / AX, y / BY)
    g = math.hypot((x - XC) / AX ** 2, y / BY ** 2) / max(rho, 1e-6)
    e = (rho - 1.0) / max(g, 1e-6)
    f = x - XF
    r = FLAT_CORNER
    return min(-r, max(e, f)) + math.hypot(max(r + e, 0.0), max(r + f, 0.0))


def housing_z(x, y):
    """The shell's top: the dome, the eye's socket and brow, the crease, the jaw's ridge, the lip along the flat side
    and its rounded edge."""
    z = dome(x, y)
    if z <= 0.0:
        return 0.05
    grow = smoothstep(0.0, 3.0, z)      # the details fade out down the dome's foot
    e = eye_e(x, y)
    if e < 1.0:
        z -= SOCKET_DEPTH * (1.0 - e * e) ** 1.5
    z += BROW * math.exp(-((e - 1.12) / 0.2) ** 2)
    z -= CREASE_D * math.exp(-(CREASE_DIST(x, y) / CREASE_W) ** 2) * grow
    z += JAW_H * math.exp(-(JAW_DIST(x, y) / JAW_W) ** 2) * grow
    z -= GILL_D * math.exp(-(GILL_DIST(x, y) / GILL_W) ** 2) * grow
    d = max(0.0, -plan_sdf(x, y))
    flat = smoothstep(XF - 3.5, XF - 2.0, x)
    z += LIP[0] * math.exp(-((d - LIP[1]) / LIP[2]) ** 2) * grow * flat
    if d < EDGE_R:
        z -= EDGE_R - math.sqrt(max(0.0, EDGE_R * EDGE_R - (EDGE_R - d) ** 2))
    return max(z, 0.05)


def plan_ring(d, spacing):
    """The plan's outline moved d inwards (where plan_sdf is -d), counter-clockwise, about `spacing` apart."""
    cx, cy = PLAN_CENTRE
    pts = []
    for i in range(720):
        a = 2 * math.pi * i / 720
        c, s = math.cos(a), math.sin(a)
        lo, hi = 0.0, 40.0
        for _ in range(30):
            mid = (lo + hi) / 2
            if plan_sdf(cx + mid * c, cy + mid * s) < -d:
                lo = mid
            else:
                hi = mid
        pts.append((cx + lo * c, cy + lo * s))
    return ccw(resample(pts, spacing))


def eye_ring(e, spacing):
    ex, ey, rx, ry, tilt = EYE
    a = math.radians(tilt)
    pts = []
    for i in range(96):
        t = 2 * math.pi * i / 96
        lx, ly = e * rx * math.cos(t), e * ry * math.sin(t)
        pts.append((ex + lx * math.cos(a) - ly * math.sin(a), ey + lx * math.sin(a) + ly * math.cos(a)))
    return resample(pts, spacing)


def housing_shell(m):
    """The shell: a solid over the plan, its top at housing_z, straight walls down to the skirt, a flat underside.
    Its top is triangulated over rows of points following its features (the outline, the flat side's edge and lip,
    the socket, the crease, the jaw's ridge), so they come out smooth, and coloured by bands of its tone (cut along
    smooth contours); the walls and the underside are a second object."""
    outline = plan_ring(0.0, 0.42)
    pool = Thinned(0.2)
    for p in outline:
        pool.add(p, 0.05)
    for line, offsets in ((CREASE_LINE, (0.0, 0.22, -0.22, 0.48, -0.48, 0.9, -0.9)),
                          (JAW_LINE, (0.0, 0.6, -0.6, 1.3, -1.3)), (GILL_LINE, (0.0, 0.2, -0.2, 0.5, -0.5))):
        for o in offsets:
            for p in open_resample(offset_curve(line, o), 0.42):
                if plan_sdf(*p) < -0.3:
                    pool.add(p, 0.14)
    for e, spacing in ((0.4, 0.5), (0.75, 0.42), (1.0, 0.34), (1.15, 0.34), (1.3, 0.38), (1.55, 0.5)):
        for p in eye_ring(e, spacing):
            if plan_sdf(*p) < -0.3:
                pool.add(p, 0.16)
    for d, spacing in ((0.12, 0.45), (0.35, 0.48), (0.65, 0.52), (1.0, 0.58), (1.5, 0.64)):
        for p in plan_ring(d, spacing):
            pool.add(p, 0.24)
    for p in lattice(-24.0, 0.0, -23.0, 23.0, 0.8):
        if plan_sdf(*p) < -2.0:
            pool.add(p, 0.45)
    points = pool.points
    n = len(outline)
    edges = [(i, (i + 1) % n) for i in range(n)]
    verts, _e, faces, *_ = geometry.delaunay_2d_cdt([Vector(p) for p in points], edges, [], 0, 1e-6)
    tris = [f for f in faces if len(f) == 3 and
            plan_sdf(sum(verts[i].x for i in f) / 3, sum(verts[i].y for i in f) / 3) < 0]
    top = k.mesh_object("shell", [(v.x, v.y, housing_z(v.x, v.y)) for v in verts], [tuple(f) for f in tris])
    bm = bmesh.new()
    bm.from_mesh(top.data)
    for v in [v for v in bm.verts if not v.link_faces]:
        bm.verts.remove(v)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    for f in bm.faces:                  # facing up
        if f.normal.z < 0:
            f.normal_flip()
    bm.verts.index_update()
    rim = [e for e in bm.edges if len(e.link_faces) == 1]
    # The walls down from the top's rim and the flat underside.
    walls = bmesh.new()
    upper, lower = {}, {}
    for e in rim:
        for v in e.verts:
            if v.index not in upper:
                upper[v.index] = walls.verts.new(v.co)
                lower[v.index] = walls.verts.new((v.co.x, v.co.y, -SKIRT))
    for e in rim:
        a, b = (v.index for v in e.verts)
        walls.faces.new([upper[b], upper[a], lower[a], lower[b]])
    loop = sorted(lower.values(), key=lambda v: math.atan2(v.co.y - PLAN_CENTRE[1], v.co.x - PLAN_CENTRE[0]))
    walls.faces.new(loop)
    bmesh.ops.triangulate(walls, faces=walls.faces[:])
    bmesh.ops.recalc_face_normals(walls, faces=walls.faces)
    bm.to_mesh(top.data)
    bm.free()
    wall = k.mesh_object("shell_wall", [], [], m["wall"])
    walls.to_mesh(wall.data)
    walls.free()
    names = []
    for poly in top.data.polygons:
        key = housing_paint(poly.center.x, poly.center.y)
        if key not in names:
            names.append(key)
            top.data.materials.append(m[key])
        poly.material_index = names.index(key)
    face_out(top, lambda c: Vector((0.0, 0.0, 1.0)))
    face_out(wall, lambda c: Vector((c.x - PLAN_CENTRE[0], c.y - PLAN_CENTRE[1], 0.0)) if c.z > -SKIRT + 0.01 else
             Vector((0.0, 0.0, -1.0)))
    k.smooth(top, 50)
    k.smooth(wall, 30)
    return [top, wall]


def face_out(obj, outward):
    """Turns an open surface (consistently wound) to face the way outward(centre) says, on the whole."""
    mesh = obj.data
    score = sum(p.normal.dot(outward(p.center)) * p.area for p in mesh.polygons)
    if score < 0:
        mesh.flip_normals()
        mesh.update()


def signed_side(line, x, y):
    """The distance to an open polyline, positive to the right of its direction."""
    best, sign = 1e9, 1.0
    for (ax, ay), (bx, by) in zip(line, line[1:]):
        dx, dy = bx - ax, by - ay
        t = max(0.0, min(1.0, ((x - ax) * dx + (y - ay) * dy) / max(dx * dx + dy * dy, 1e-12)))
        d = math.hypot(x - ax - t * dx, y - ay - t * dy)
        if d < best:
            best, sign = d, -1.0 if dx * (y - ay) - dy * (x - ax) > 0 else 1.0
    return best * sign


def housing_paint(x, y):
    """The shell's colours, face by face (their borders follow the rows of points laid along the features): the
    socket and its lit rim, the crease, the lip along the flat side, the jaw's ridge lit, the cheek below the crease
    and above the jaw a shade darker, the rest the steel's middle shade."""
    e = eye_e(x, y)
    if e < 1.0:
        return "socket"
    if e < 1.3 and eye_coords(x, y)[0] < 0.2:
        return "shell_hi"                       # the socket's rim, lit on its left
    if dome(x, y) < 1.0:
        return "shell"
    crease = signed_side(CREASE_LINE, x, y)     # positive below the crease (its right)
    if abs(crease) < 0.22 or GILL_DIST(x, y) < 0.2:
        return "groove"
    d = -plan_sdf(x, y)
    if x > XF - 2.5 and abs(y) < 18.6 and 0.3 < d < 0.95:
        return "lip"
    jaw = -signed_side(JAW_LINE, x, y)          # positive above the jaw (its left)
    if abs(jaw) < 0.6:
        return "shell_hi"
    if crease > 0.9 and jaw > 1.3:
        return "shell_lo"
    return "shell"


def housing_materials():
    glow = k.level_palette()
    steel = dict(metallic=0.5, roughness=0.32)
    return {
        "shell": k.material("fgate_shell", palette=0x69, **steel),
        "shell_lo": k.material("fgate_shell_lo", palette=0x67, **steel),
        "shell_hi": k.material("fgate_shell_hi", palette=0x6a, **steel),
        "wall": k.material("fgate_wall", palette=0x66, metallic=0.5, roughness=0.36),
        "groove": k.material("fgate_groove", palette=0x64, metallic=0.4, roughness=0.45),
        "socket": k.material("fgate_socket", palette=0x65, metallic=0.4, roughness=0.4),
        "lip": k.material("fgate_lip", palette=0x6b, metallic=0.55, roughness=0.28),
        "rib": k.material("fgate_rib", palette=0x6d, metallic=0.55, roughness=0.25),
        "rib_side": k.material("fgate_rib_side", palette=0x6b, metallic=0.55, roughness=0.28),
        "eye": k.material("fgate_eye", palette=0x61, metallic=0.3, roughness=0.06),
        "glint": k.material("fgate_glint", palette=0x6e, metallic=0.1, roughness=0.1, emission=glow[0x6d],
                            emission_strength=0.6),
    }


def rib(name, path, hw, proud, m, hit):
    """A rib laid along a path on the shell: rounded-box sections standing `proud` out of it, its ends rounded
    down."""
    line = open_resample(mk.chaikin(path, 2, closed=False) if len(path) > 2 else path, 0.45)
    points, ups = [], []
    for x, y in line:
        h = hit(x, y)
        points.append(Vector((x, y, h[0].z if h else housing_z(x, y))))
        ups.append(h[1] if h else Vector((0, 0, 1)))
    segments = 12
    bar = mk.bar(name, points, ups, hw, proud, 0.7, m["rib"], segments, 2.6)
    count = len(points)
    # Lit along its top, its flanks a shade darker: cut along the sections' angle (smooth borders).
    tops = [math.sin(2 * math.pi * (i % segments) / segments) for i in range(count * segments)] + [0.0, 0.0]
    length = sum(math.dist(a, b) for a, b in zip(line, line[1:]))
    end = min(0.45, 0.6 / length)
    for i, v in enumerate(bar.data.vertices):
        t = (i // segments) / (count - 1) if i < count * segments else float(i - count * segments)
        f = min(1.0, t / end, (1 - t) / end)
        base = housing_z(v.co.x, v.co.y)
        if v.co.z > base:
            v.co.z = base + (v.co.z - base) * (0.35 + 0.65 * math.sqrt(max(0.0, f)))
    bar.data.update()
    band_split(bar, tops, [(-9.0, m["rib_side"]), (0.45, m["rib"])])
    k.smooth(bar, 60)
    return bar


def knob(m):
    x, y, r, up = KNOB
    z0 = housing_z(x, y)
    obj = mk.lathe("knob", [(r + 0.15, z0 - 0.9), (r + 0.15, z0 + 0.05), (r, z0 + 0.2), (r, z0 + up - 0.45),
                            (r - 0.25, z0 + up - 0.12), (r - 0.65, z0 + up + 0.04), (0.45, z0 + up + 0.16),
                            (0.01, z0 + up + 0.18)], (x, y), m["rib"], 20)
    k.smooth(obj, 50)
    mk.paint(obj, lambda c, n: m["groove"] if c.z < z0 + 0.25 else m["rib_side"] if n.z < 0.6 else None)
    return obj


def surface_frame(normal, tilt):
    """A turn whose z is the normal and whose x lies along the screen's x (as far as the normal allows), turned
    `tilt` degrees about the normal."""
    n = Vector(normal).normalized()
    x = Vector((1.0, 0.0, 0.0))
    x = (x - n * x.dot(n)).normalized()
    y = n.cross(x)
    frame = Matrix((x, y, n)).transposed().to_4x4()
    return frame @ Matrix.Rotation(math.radians(tilt), 4, "Z")


def eye_parts(m, hit):
    ex, ey, rx, ry, tilt = EYE
    h = hit(ex, ey)
    normal = h[1] if h else Vector((0, 0, 1))
    floor = h[0] if h else Vector((ex, ey, housing_z(ex, ey)))
    turn = surface_frame(normal, tilt)
    lens = mk.ball("eye", (0.0, 0.0, 0.0), (rx * 0.82, ry * 0.82, 1.05), m["eye"], 28, 12)
    lens.data.transform(Matrix.Translation(floor + normal * 0.35) @ turn)
    glint = mk.ball("glint", (0.0, 0.0, 0.0), (0.42, 0.6, 0.25), m["glint"], 14, 7)
    glint.data.transform(Matrix.Translation(floor + normal * 1.3) @ turn @ Matrix.Translation((0.55, -0.35, 0.0)))
    x, y = RIVET
    rivet = mk.dome("rivet", (x, y), (0.62, 0.62, 0.45), housing_z(x, y) - 0.1, m["rib"], 16, 5)
    return [lens, glint, rivet]


def build_housing():
    m = housing_materials()
    shell = housing_shell(m)
    bpy.context.view_layer.update()
    hit = mk.surface(shell[:1])
    parts = shell + [rib(name, path, hw, proud, m, hit) for name, path, hw, proud in RIBS] + [knob(m)]
    parts += eye_parts(m, hit)
    for obj in parts:
        mk.apply(obj)
    if k.args().get("stats") == "1":
        for obj in parts:
            print("   %-14s %6d triangles" % (obj.name, mk.triangles([obj])))
    return parts, m


# --- Checks, previews, export ----------------------------------------------------------------------------------------

def gate_mask(sheet, housing, flap, side):
    """The sprites of a gate as the levels put them together (48 x 56)."""
    mask = [[False] * 48 for _ in range(56)]
    left, right = (housing, flap) if side == "left" else (flap, housing)
    for (top, bottom), c0 in ((left, 0), (right, 24)):
        for sprite, r0 in ((top, 0), (bottom, 28)):
            part = k.sprite_mask(sheet, sprite)
            for r in range(28):
                for c in range(24):
                    if part[r][c]:
                        mask[r0 + r][c0 + c] = True
    return mask


def mirror_objects(objects):
    flip = Matrix.Scale(-1, 4, (1, 0, 0))
    for obj in objects:
        obj.data.transform(flip)
        obj.data.flip_normals()
        obj.data.update()


def export_pieces(objects, centres, names, cap, out, sheet, options, only):
    """Cuts objects at y = 0 into the top and bottom sprites' pieces, each moved to its sprite's centre, exported."""
    for (name, sprite), (cx, cy) in zip(names, centres):
        if only and name not in only:
            continue
        box = (-40.0, 40.0, 0.0, 40.0) if cy > 0 else (-40.0, 40.0, -40.0, 0.0)
        pieces = [p for p in (cut(src, box, cap) for src in objects) if p is not None]
        mk.transform(pieces, Matrix.Translation((-cx, -cy, 0.0)))
        bpy.context.view_layer.update()
        if sheet:
            mk.compare("%s (A %d)" % (name, sprite), mk.coverage(pieces, 24, 28), k.sprite_mask(sheet, sprite))
        mk.report(name, pieces, os.path.join(out, name + ".glb"))
        if "preview" in options and options.get("pieces") == "1":
            mk.preview(options["preview"] + name, pieces)
        for o in pieces:
            bpy.data.objects.remove(o)


def build():
    options = k.args()
    out = mk.outdir(options)
    only = options["only"].split(",") if "only" in options else None
    sheets = options.get("check")
    sheet = (os.path.join(sheets, "enemy_A.png") if os.path.isdir(sheets) else sheets) if sheets else None
    heat = Heat()
    for side in options.get("sides", "left,right").split(","):
        k.reset()
        bpy.context.scene.view_settings.view_transform = "Standard"   # previews in the game's colours
        housing, hm = build_housing()
        if side == "right":
            mirror_objects(housing)
        bpy.context.view_layer.update()
        low, high = mk.bounds(housing)
        print("== housing (%s gate): %d triangles, x %.2f..%.2f y %.2f..%.2f z %.2f..%.2f" % (
            side, mk.triangles(housing), low.x, high.x, low.y, high.y, low.z, high.z))
        bpy.context.view_layer.update()
        export_pieces(housing, [c for _, _, c in HOUSINGS[side]], [(n, s) for n, s, _ in HOUSINGS[side]], hm["wall"],
                      out, sheet, options, only)
        for degrees, left_names, right_names in FRAMES:
            names = left_names if side == "left" else right_names
            if only and not any(n in only for n, _ in names) and "preview" not in options:
                continue
            flap, fm = build_flap(degrees, heat)
            if side == "right":
                mirror_objects(flap)
            bpy.context.view_layer.update()
            low, high = mk.bounds(flap)
            print("== flap %.0f degrees (%s gate): %d triangles, x %.2f..%.2f y %.2f..%.2f z %.2f..%.2f" % (
                degrees, side, mk.triangles(flap), low.x, high.x, low.y, high.y, low.z, high.z))
            whole = housing + flap
            if sheet:
                mk.compare("whole %s gate, flap %.0f degrees" % (side, degrees), mk.coverage(whole, 48, 56),
                           gate_mask(sheet, [s for _, s, _ in HOUSINGS[side]], [s for _, s in names], side))
            if "preview" in options:
                mk.preview(options["preview"] + "gate_%s_%d" % (side, round(degrees)), whole, size=(48, 56), scale=10,
                           distance=1.9)
            export_pieces(flap, FLAP_CENTRES[side], names, fm["cap"], out, sheet, options, only)
            for o in flap:
                bpy.data.objects.remove(o)


if __name__ == "__main__":
    build()
