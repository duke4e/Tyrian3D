"""The green WARNING sign of FLEET (episode 3, sky layer) and LAVA RUN (episode 4, ground layer) that comes before the
wall of fire: sheet K sprites 121 (left) and 123 (right), 2x2 each: one 48 x 28 picture; enemies 711 and 712; one
frame each), polished (2026-10-19; it replaces wave3_o.py's warning_whole() and warning_piece(), strokes inflated from
the pixels' outlines). models.cfg: model warning_left / warning_right ... origin; sprite k 121 warning_left yaw=0,
sprite k 123 warning_right yaw=0. The levels put the halves side by side: 711 (121) at x and 712 (123) at x + 24, at
the same y (FLEET's events 2600-4100, LAVA RUN's 2000-2700).

As the sprite draws it (columns and rows of the picture): the word WARNING in a blocky pixel font, letters seven rows
tall (rows 13-19) and one pixel thick, shaded down their height like chrome (row 13 darkest, rows 16-17 brightest, a
dark band at row 18); W columns 2-6, A 8-10, R 12-14, N 16-19, I 21-23, N 25-28, G 30-33. Under it a line (row 21,
columns 2-34, a highlight round column 9) that turns up the right side (column 35, rows 12-20), back left along row
11 and up to the left in a thicker diagonal (columns 25-30 of rows 6-10) into the shaft of an arrow whose head
points up the screen (rows 0-7, columns 19-31: a chevron, brightest at its tip), where the fire comes from. Every
stroke is outlined in near-black green (index 0x20), so the letters lie on a dark backing following them. The white
dot packed into the right sprite's corner (columns 41-44 of rows 5-8) is CAMANIS' spark, K 124: left out.

Built as a neon-lit sign plate (polish_machine_kit): the backing is a dark green plate whose outline is the strokes'
outline grown by the sprite's dark border (a distance field round the strokes, contoured), its top edge bevelled;
the letters, the line and the arrow head are strokes standing on it (each glyph the union of its strokes' prisms,
exact booleans, its top edges bevelled), glowing in their own greens: the letters cut into bands down their height
as the sprite shades them, the line darker along its sides with the underline's highlight, the arrow head brightest
at its tip. The whole sign is then cut along the sprites' edge (x = 0; polish_arch.py's cut()), each piece moved so
its sprite's centre is its origin. It lies flat, facing up at the camera, its base on its layer (no height needed:
in FLEET it floats among the ships; in LAVA RUN it hovers its layer's 4 pixels over the lava like a sign).

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera; the whole's
origin is the edge between the two sprites at their middle (column c of the picture is x = c + 0.5 - 24, row r is
y = 13.5 - r).

Replaces wave3_o.py's warning sign: remove WARN_PIECES, warning_whole() (its @o.whole("warning", ...) registration),
warning_piece() and the loop registering warning_left / warning_right (and the sign's lines of its docstring and
usage), and wave3_o_art.py's WARN (nothing else reads it), so that they don't overwrite these models.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouettes of the
whole and of each half against enemy_K.png, the spark's pixels left out), --preview <prefix>.
"""
import math
import os
import sys

import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k  # noqa: E402
from polish_arch import cut  # noqa: E402  (polish_machine_kit.cut without its material indices shifted twice)
from polish_orb_red import band_split  # noqa: E402

PIECES = [("warning_left", 121, (-24.0, 0.0, -14.0, 14.0)), ("warning_right", 123, (0.0, 24.0, -14.0, 14.0))]
SPARK = (41, 44, 5, 8)          # the spark's pixels in the picture (columns, rows): not the sign's


def C(c, r):
    """The centre of the picture's pixel (c, r) (fractions allowed)."""
    return (c + 0.5 - 24.0, 13.5 - r)


# The strokes, by pixel centres (column, row): each a segment from one pixel's centre to another's, covering the
# pixels between (square ends half a pixel beyond them).
LETTERS = {
    "W": [((2, 13), (2, 19)), ((6, 13), (6, 19)), ((4, 15), (4, 19)), ((2, 19), (6, 19))],
    "A": [((8, 13), (8, 19)), ((10, 13), (10, 19)), ((8, 13), (10, 13)), ((8, 16), (10, 16))],
    "R": [((12, 13), (12, 19)), ((12, 13), (13, 13)), ((13, 13), (14, 14)), ((14, 14), (14, 15)), ((14, 15), (13, 16)),
          ((12, 16), (13, 16)), ((13, 16), (14, 17)), ((14, 17), (14, 19))],
    "N1": [((16, 13), (16, 19)), ((19, 13), (19, 19)), ((16, 13), (19, 16))],
    "I": [((21, 13), (22.9, 13)), ((22, 13), (22, 19)), ((21, 19), (22.9, 19))],
    "N2": [((25, 13), (25, 19)), ((28, 13), (28, 19)), ((25, 13), (28, 16))],
    "G": [((31, 13), (32, 13)), ((31, 13), (30, 14)), ((30, 14), (30, 18)), ((30, 18), (31, 19)), ((31, 19), (32, 19)),
          ((32, 19), (33, 18)), ((33, 18), (33, 16)), ((33, 16), (32, 16))],
}
STROKE_W = 1.0                  # the letters' strokes are a pixel wide
# The line: under the word, up the right side, back along row 11, up the diagonal into the arrow's shaft; (from, to,
# width).
LINE = [((2, 21), (33.3, 21), 1.0), ((33.3, 21), (35, 19.3), 1.0), ((35, 19.3), (35, 12.7), 1.0),
        ((35, 12.7), (33.3, 11), 1.0), ((33.3, 11), (30, 11), 1.0), ((30, 11), (25, 6), 1.5),
        ((25, 6), (25, 2.2), 1.05)]
HIGHLIGHT = (9.0, 2.6)          # the underline's highlight: its column, half its length
# The arrow's head: a chevron from its tip down to the arms' ends.
TIP, ARM_ENDS, ARM_W = (25, 1.05), [(20.1, 5.95), (29.9, 5.95)], 1.45
# The letters' bands down their height (rows 13-19): from this row (at the pixels' top edges), this green.
BANDS = [(13, 0xc3), (14, 0xc5), (15, 0xc7), (16, 0xc8), (17, 0xc9), (18, 0xc4), (19, 0xc5)]
HEAD_BANDS = [(0.0, 0xca), (1.6, 0xc8), (2.7, 0xc7), (3.9, 0xc6), (5.1, 0xc3)]   # by distance from the tip
PLATE_GROW = 1.32               # the plate's outline: this far round the strokes' middle lines
PLATE_Z = (-0.35, 0.62)         # its bottom and top
STROKE_Z = (0.3, 1.45)          # the strokes' bottom (sunk in the plate) and top
BEVEL = 0.2                     # the strokes' top edges


def materials():
    glow = k.level_palette()

    def lit(index, strength, roughness=0.25):
        return k.material(f"warn_green_{index:x}", palette=index, metallic=0.0, roughness=roughness,
                          emission=glow[index], emission_strength=strength)
    m = {
        "plate": k.material("warn_plate", palette=0x20, metallic=0.35, roughness=0.3),
        "plate_edge": k.material("warn_plate_edge", palette=0x21, metallic=0.35, roughness=0.3),
    }
    for index in sorted({b[1] for b in BANDS} | {b[1] for b in HEAD_BANDS} | {0xc1, 0xc9, 0xcb}):
        m[index] = lit(index, 0.55 + 0.05 * (index - 0xc0))
    return m


# --- The strokes -------------------------------------------------------------------------------------------------

def stroke_prism(name, a, b, width, z0, z1, ends=0.5, end=None):
    """A prism along the segment a-b (picture pixel centres), width across, `ends` past its start (and `end`, or
    `ends`, past its end)."""
    pa, pb = Vector(C(*a)), Vector(C(*b))
    d = pb - pa
    if d.length < 1e-6:
        d = Vector((1.0, 0.0))
    d.normalize()
    side = Vector((-d.y, d.x)) * (width / 2)
    pa, pb = pa - d * ends, pb + d * (ends if end is None else end)
    outline = [tuple(pa - side), tuple(pb - side), tuple(pb + side), tuple(pa + side)]
    return mk.prism(name, outline, z0, z1)


def union(name, parts, mat):
    """The union of prisms (exact booleans), its coplanar faces merged."""
    body = parts[0]
    body.name = name
    body.data.materials.clear()
    body.data.materials.append(mat)
    if len(parts) > 1:
        mk.boolean(body, parts[1:], "UNION")
    mk.cleanup(body)
    return body


def orthogonal(a, b):
    return abs(a[0] - b[0]) < 1e-6 or abs(a[1] - b[1]) < 1e-6


def glyph(name, segments, mat):
    """A letter: the union of its strokes (square ends half a pixel past the pixel centres on the upright and level
    ones, as the pixels are; the slanting ones end at the centres, inside their neighbours), its top edges bevelled,
    triangulated (for cutting into bands)."""
    parts = [stroke_prism(f"{name}_{i}", a, b, STROKE_W, *STROKE_Z, ends=0.5 if orthogonal(a, b) else 0.0)
             for i, (a, b) in enumerate(segments)]
    body = union(name, parts, mat)
    mk.bevel(body, BEVEL, 2, 35)
    return triangulated(body)


def triangulated(obj):
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.triangulate(bm, faces=bm.faces[:], quad_method="BEAUTY", ngon_method="BEAUTY")
    bm.to_mesh(obj.data)
    bm.free()
    return obj


def disc(name, centre, radius, z0, z1, segments=20):
    cx, cy = centre
    return mk.prism(name, [(cx + radius * math.cos(2 * math.pi * j / segments),
                            cy + radius * math.sin(2 * math.pi * j / segments)) for j in range(segments)], z0, z1)


def letters(m):
    """The word: each letter the union of its strokes, bevelled, cut into bands down its height."""
    first = m[BANDS[0][1]]
    for name, segments in LETTERS.items():
        body = glyph("letter_" + name, segments, first)
        values = [13.5 - v.co.y + 0.5 for v in body.data.vertices]   # the picture's row (at the pixels' top edges)
        band_split(body, values, [(-99.0 if i == 0 else row, m[index]) for i, (row, index) in enumerate(BANDS)])
        mk.shade(body, 35)


def line(m):
    """The line from under the word round to the arrow's shaft: one glyph, its sides darker, a highlight on the
    underline round column 9."""
    # Its segments end at the joints, round discs fill the joints; the free start square.
    parts = [stroke_prism(f"line_{i}", a, b, w, *STROKE_Z, ends=0.5 if i == 0 else 0.0, end=0.0)
             for i, (a, b, w) in enumerate(LINE)]
    for i in range(len(LINE) - 1):
        w = max(LINE[i][2], LINE[i + 1][2])
        parts.append(disc(f"line_joint{i}", C(*LINE[i][1]), w / 2, *STROKE_Z))
    body = union("line", parts, m[0xc5])
    mk.bevel(body, BEVEL, 2, 35)
    # Cut its faces across round the highlight, then paint: the top faces there brighter, the sloping sides dark.
    hx, half = HIGHLIGHT
    x9 = hx + 0.5 - 24.0
    bm = bmesh.new()
    bm.from_mesh(body.data)
    for dx in (-half, -half * 0.6, -half * 0.25, half * 0.25, half * 0.6, half):
        bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-5,
                               plane_co=(x9 + dx, 0, 0), plane_no=(1, 0, 0))
    bm.to_mesh(body.data)
    bm.free()
    y21 = C(0, 21)[1]

    def pick(c, n):
        if n.z < 0.75:
            return m[0xc1]
        if abs(c.y - y21) < 0.6 and abs(c.x - x9) < half:
            t = abs(c.x - x9) / half
            return m[0xcb] if t < 0.25 else m[0xc9] if t < 0.6 else m[0xc7]
        return None
    mk.paint(body, pick)
    mk.shade(body, 35)


def head(m):
    """The arrow's head: a chevron of two arms from the tip, bevelled, brightest at its tip."""
    parts = [stroke_prism(f"head_{i}", TIP, end, ARM_W, *STROKE_Z, ends=0.55) for i, end in enumerate(ARM_ENDS)]
    body = union("head", parts, m[HEAD_BANDS[0][1]])
    # Its point: trimmed square across the top (the two arms' ends overshoot into a peak).
    tip = Vector(C(*TIP))
    mk.boolean(body, mk.box("head_trim", tip.x - 3, tip.x + 3, tip.y + 0.62, tip.y + 4, -2, 4), "DIFFERENCE")
    mk.cleanup(body)
    mk.bevel(body, BEVEL, 2, 35)
    triangulated(body)
    values = [(Vector((v.co.x, v.co.y)) - tip).length for v in body.data.vertices]
    band_split(body, values, [(-99.0 if i == 0 else d, m[index]) for i, (d, index) in enumerate(HEAD_BANDS)])
    mk.shade(body, 35)


# --- The plate ----------------------------------------------------------------------------------------------------

def all_segments():
    segs = []
    for segments in LETTERS.values():
        segs += [(C(*a), C(*b), STROKE_W) for a, b in segments]
    segs += [(C(*a), C(*b), w) for a, b, w in LINE]
    segs += [(C(*TIP), C(*end), ARM_W) for end in ARM_ENDS]
    return segs


def contours(field, xs, ys, level=0.0):
    """Marching squares: the closed polylines where field (rows along ys, columns along xs) crosses level, each a
    list of (x, y); outlines run one way round, holes the other."""
    f = field - level
    ny, nx = f.shape

    def point(edge):
        kind, i, j = edge
        if kind == "h":   # between (i, j) and (i, j + 1)
            a, b = f[i, j], f[i, j + 1]
            t = a / (a - b)
            return (xs[j] + t * (xs[j + 1] - xs[j]), ys[i])
        a, b = f[i, j], f[i + 1, j]
        t = a / (a - b)
        return (xs[j], ys[i] + t * (ys[i + 1] - ys[i]))
    nxt = {}
    for i in range(ny - 1):
        for j in range(nx - 1):
            v = [f[i, j] > 0, f[i, j + 1] > 0, f[i + 1, j + 1] > 0, f[i + 1, j] > 0]
            if all(v) or not any(v):
                continue
            bottom, right, top, left = ("h", i, j), ("v", i, j + 1), ("h", i + 1, j), ("v", i, j)
            edges = [(bottom, v[0], v[1]), (right, v[1], v[2]), (top, v[2], v[3]), (left, v[3], v[0])]
            # Walking the cell's edges counter-clockwise (bottom, right, top, left), a segment leaves the inside where
            # an edge goes from inside to outside and enters where it goes from outside to inside.
            outs = [e for e, a, b in edges if a and not b]
            ins = [e for e, a, b in edges if not a and b]
            if len(outs) == 1:
                nxt[ins[0]] = outs[0]
            else:  # a saddle: decide by the middle
                middle = (f[i, j] + f[i, j + 1] + f[i + 1, j + 1] + f[i + 1, j]) / 4 > 0
                order = [e for e, a, b in edges]
                for e_in in ins:
                    k_in = order.index(e_in)
                    if middle:
                        # The inside joins across: follow round to the next exit.
                        for step in range(1, 4):
                            cand = order[(k_in + step) % 4]
                            if cand in outs:
                                nxt[e_in] = cand
                                break
                    else:
                        for step in range(1, 4):
                            cand = order[(k_in - step) % 4]
                            if cand in outs:
                                nxt[e_in] = cand
                                break
    loops = []
    seen = set()
    for start in list(nxt):
        if start in seen:
            continue
        loop, e = [], start
        while e not in seen and e in nxt:
            seen.add(e)
            loop.append(point(e))
            e = nxt[e]
        if len(loop) > 2:
            loops.append(loop)
    return loops


def simplify(points, tolerance):
    """Douglas-Peucker on a closed polyline."""
    def dp(pts):
        if len(pts) < 3:
            return pts
        a, b = Vector(pts[0]), Vector(pts[-1])
        ab = b - a
        best, index = -1.0, 0
        for i in range(1, len(pts) - 1):
            p = Vector(pts[i])
            if ab.length < 1e-9:
                dist = (p - a).length
            else:
                dist = abs(ab.x * (p.y - a.y) - ab.y * (p.x - a.x)) / ab.length
            if dist > best:
                best, index = dist, i
        if best <= tolerance:
            return [pts[0], pts[-1]]
        return dp(pts[:index + 1])[:-1] + dp(pts[index:])
    # Split at the point farthest from the first so both halves are open runs.
    far = max(range(len(points)), key=lambda i: (Vector(points[i]) - Vector(points[0])).length)
    first = dp(points[:far + 1])
    second = dp(points[far:] + [points[0]])
    return first[:-1] + second[:-1]


def area(points):
    return 0.5 * sum(points[i][0] * points[(i + 1) % len(points)][1] - points[(i + 1) % len(points)][0] *
                     points[i][1] for i in range(len(points)))


def plate(m):
    """The dark backing: the outline of everything within PLATE_GROW of the strokes' middle lines (round them as the
    sprite's dark border is), a plate under it, its top edge bevelled. The few small holes the outline leaves between
    the letters are filled: the sprite's border is solid there."""
    step = 0.1
    xs = np.arange(-25.0, 25.0 + step / 2, step)
    ys = np.arange(-15.0, 15.0 + step / 2, step)
    X, Y = np.meshgrid(xs, ys)
    D = np.full(X.shape, 1e9)
    for (ax, ay), (bx, by), w in all_segments():
        dx, dy = bx - ax, by - ay
        l2 = dx * dx + dy * dy
        t = np.clip(((X - ax) * dx + (Y - ay) * dy) / l2, 0.0, 1.0) if l2 > 0 else np.zeros(X.shape)
        # The letters' square ends: half a pixel past each end along the segment counts as on it.
        dist = np.hypot(X - (ax + t * dx), Y - (ay + t * dy))
        D = np.minimum(D, dist - (w - STROKE_W) / 2)
    loops = [simplify(loop, 0.035) for loop in contours(PLATE_GROW - D, xs, ys)]
    loops = [loop for loop in loops if abs(area(loop)) > 0.3]
    # The outlines run one way round, the holes the other: the largest is an outline.
    sign = math.copysign(1.0, area(max(loops, key=lambda loop: abs(area(loop)))))
    outer = [loop for loop in loops if area(loop) * sign > 0]
    holes = [loop for loop in loops if area(loop) * sign < 0]
    bodies = []
    for i, loop in enumerate(outer):
        body = mk.prism(f"plate{i}", loop, PLATE_Z[0], PLATE_Z[1], m["plate"])
        mk.cleanup(body, dissolve=0.0)
        mk.bevel(body, 0.24, 2, 45)
        mk.shade(body, 40)
        mk.paint(body, lambda c, n: m["plate_edge"] if 0.2 < n.z < 0.9 else None)
        bodies.append(body)
    print("plate: %d outlines (%d points), %d small holes filled" % (len(outer), sum(len(o) for o in outer),
                                                                      len(holes)))
    return bodies


def build_whole():
    m = materials()
    plate(m)
    letters(m)
    line(m)
    head(m)
    whole = mk.meshes()
    for obj in whole:
        mk.apply(obj)
    bpy.context.view_layer.update()
    return whole, m


def sprite_mask(sheet, sprite, c0):
    """The sprite's pixels, the spark's left out."""
    mask = k.sprite_mask(sheet, sprite)
    s0, s1, r0, r1 = SPARK
    for r in range(r0, r1 + 1):
        for c in range(s0, s1 + 1):
            if 0 <= c - c0 < 24:
                mask[r][c - c0] = False
    return mask


def whole_mask(sheet):
    mask = [[False] * 48 for _ in range(28)]
    for sprite, c0 in ((121, 0), (123, 24)):
        part = sprite_mask(sheet, sprite, c0)
        for y in range(28):
            for x in range(24):
                if part[y][x]:
                    mask[y][c0 + x] = True
    return mask


def build():
    k.reset()
    options = k.args()
    out = mk.outdir(options)
    whole, m = build_whole()
    print("whole sign: %d triangles, %d objects" % (mk.triangles(whole), len(whole)))
    sheet = os.path.join(options["check"], "enemy_K.png") if "check" in options else None
    if sheet:
        mk.compare("whole (K 121 + 123, the spark left out)", mk.coverage(whole, 48, 28), whole_mask(sheet))
    bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
    if "preview" in options:
        mk.preview(options["preview"] + "warning_whole", whole, size=(48, 28), scale=8, distance=1.7)
    for name, sprite, box in PIECES:
        pieces = [p for p in (cut(src, box, m["plate"]) for src in whole) if p is not None]
        mk.transform(pieces, Matrix.Translation((-(box[0] + box[1]) / 2, 0, 0)))
        bpy.context.view_layer.update()
        for src in whole:
            src.hide_render = True
        if sheet:
            mk.compare("%s (K %d)" % (name, sprite), mk.coverage(pieces, 24, 28),
                       sprite_mask(sheet, sprite, 0 if box[0] < 0 else 24))
        mk.report(name, pieces, os.path.join(out, name + ".glb"))
        if "preview" in options:
            mk.preview(options["preview"] + name, pieces)
        for obj in pieces:
            bpy.data.objects.remove(obj)
        for src in whole:
            src.hide_render = False


if __name__ == "__main__":
    build()
