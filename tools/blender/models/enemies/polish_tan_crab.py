"""IXMUCANE's small crab (sheet 8 sprite 267, 2x2: a 23 x 19 crab in the 24 x 28 cell; enemies 102 and 103 of
episode 3, IXMUCANE: on the ground and in the sky; its animation 267 269 271), polished (2026-10-21; it replaces
wave3_y.py's tan_crab(), a sphere with lofted legs and a box for its slot). models.cfg: sprite 8 267 tan_crab yaw=0
glow=10:0.2:123 (unchanged), and frame models for the slot closing: model tan_crab_269 / tan_crab_271, frame 8 269
tan_crab_269, frame 8 271 tan_crab_271. No other enemy shows these three sprites (8 273 is enemy 192's); they are no
other sprites' pixels mirrored or in other ramps. 269 and 271 are 267's pixels moved one pixel left with the slot
narrower: two grey shutters close over it from its sides (open 5 pixels in 267, 3 in 269, 1 in 271), its glow
dimming (7d, 7b, 78 in its middle); the frame models keep the crab in place (the pixel's shift is the drawing's).

As the sprite and its 4x upscales draw it (columns and rows of the cell; symmetric about column 12, x 0.5): a dark grey
head (columns 9-15 of rows 12-18) with a wide glowing slot across its front (columns 10-14 of rows 15-17: its top
row a dark red lip, 0x71, under a grey brow (row 14); its middle burning yellow (79 7c 7d 79 76); its bottom red),
two small grey fangs under it (columns 10 and 14 of row 19); behind the head the crab's dark back, a red crest along
its top: a broad cap at its back (columns 10-14 of row 7, 72-77, hot 7c at column 12 of row 8) and a narrow glowing
fin down its middle to the brow (column 12 of rows 9-13: 77 71 78 75 72, in segments), dark gaps beside it; and on
each side two broad tan legs (ramp 1) springing from the back beside the crest (columns 8-10 and 14-16 of rows 9-11):
the inner one bending out and down to the head's side (columns 5-8 of rows 12-16), the outer one arching out to the
crab's widest (columns 1-2 and 22-23 of rows 14-17) and hanging down the screen to its tip at the bottom (columns 4-6
and 18-20 of rows 18-23), lit along their outer edges.

Built as a crab standing on its legs: the head an ellipsoid (an icosphere) with the slot sunk into its front under
the brow, glowing in rings from its hot middle, a dark lip at its top; the back a smaller dark ellipsoid behind it and
a dark belly under both (the dark gaps the sprite draws between the legs and the head); the crest a fin lofted along
the back's and the head's tops, glowing in segments, flaring into a rounded cap at the back; each leg a smooth tube of
oval section, broad across (horizontal and square to its path, so it is broad seen from above whether it reaches out
or hangs down), along an arc from its root beside the crest up and out to the crab's widest and down the screen to
its foot on the ground, a little pinched at the knee and tapering; the fangs cones. The colours are the sprite's: the
tans and greys by the light their faces get (cut into bands along smooth contours, painted from the corners' averaged
normals so that the colours meet along the cuts), the reds glowing in their own colours (emission 0.25-0.6: the cfg's
glow and the bloom add), the slot's middle hottest.
One model per frame: the same crab, its shutters (grey plates on the head's front) closing over the slot and its
glow dimming; all span the same bounds (the game centres them in height on their layer; on the ground the feet then
stand 0.3 above it).

The crab is built about u = 0 and moved to the sprite's column 12 (x 0.5, AXIS_X). Origin at the sprite's centre
(pixel 12, 14): column c is x = c + 0.5 - 12, row r is y = 13.5 - r; +Y up the screen, +Z up from the ground.

Replaces wave3_y.py's tan_crab() (its section "# --- 8 267: the small crab": CRAB and the @y.model("tan_crab", ...)
function, and the tan_crab paragraph of its docstring) and wave3_y_art.py's CRAB (nothing else reads it).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (each frame's silhouette
against its sprite in enemy_8.png, 269 and 271 shifted back the pixel; also the overlap leaving the sprite's
near-black outline ring out), --preview <prefix>, --only <name,...>.
"""
import math
import os
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
import polish_machine_kit as mk  # noqa: E402
from polish_sphere_nozzle import smoothstep, split_along  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402

AXIS_X = 0.5
SUN = Vector((-0.6, 0.6, 1.0)).normalized()

# The head: an ellipsoid (middle, radii); the slot across its front, as the sprite draws it from above (its half-width,
# its top and bottom y), sunk SLOT_DEPTH into the head, its edge rounding over SLOT_ROUND; the brow above it. The slot
# glows hottest round SLOT_HOT (a little low: its top row is the dark lip under the brow), its reds out from there by
# the distance (a fraction of its half-sizes).
HEAD = (Vector((0.0, -1.15, 3.95)), Vector((3.15, 3.45, 2.45)))
SLOT = (2.55, -1.35, -3.6)
SLOT_DEPTH, SLOT_ROUND = 0.4, 0.25
SLOT_HOT = (0.0, -2.7)
SLOT_RINGS = (0.42, 0.72, 0.9)   # the hot middle, its sides, the red (0x74), then the dark rim (0x71)
# The back behind the head (dark), under the crest and the legs' roots.
BACK = (Vector((0.0, 3.5, 4.7)), Vector((2.6, 3.15, 2.1)))
# The belly under the back and the head (dark), in the gaps between the legs and the head.
BELLY = (Vector((0.0, -0.8, 2.6)), Vector((4.6, 4.7, 1.5)))
# The crest: a fin along the tops of the head and the back from FIN_Y[0] to FIN_Y[1] (its half-width, its height over
# them), flaring into the cap at the back (an ellipsoid); the fin's segments as the sprite draws them (y, heat) and the
# cap's hot middle.
FIN_Y = (0.2, 5.6)
FIN = (0.5, 0.95)
CAP = (Vector((0.0, 6.1, 6.45)), Vector((2.65, 1.45, 1.25)))
FIN_HEAT = [(0.2, 2.0), (0.9, 2.4), (1.5, 5.0), (2.0, 5.4), (2.5, 8.0), (3.0, 7.6), (3.5, 1.4), (4.0, 1.6),
            (4.5, 7.4), (5.0, 8.6), (5.6, 11.5)]
CAP_HOT = (Vector((0.0, 5.3)), 0.5)
# The legs (the left ones; mirrored): paths (u, y, z) from the root in the back to the foot, their sections' half-widths
# (across, the other way) at the root and the tip, the joints along them (fractions of the path) where they narrow by
# PINCH. The sections are ovals, broad across (horizontally, square to the path), thinner the other way: the broad
# drooping legs the upscales draw.
LEGS = [
    ("outer", [(-1.9, 4.3, 5.6), (-5.0, 3.4, 7.0), (-7.6, 1.6, 7.2), (-9.0, -1.0, 6.2), (-9.0, -3.8, 4.4),
               (-8.0, -6.6, 2.3), (-6.8, -9.45, 0.3)],
     (1.95, 1.15), (1.35, 0.75), (0.5,)),
    ("inner", [(-1.6, 3.1, 5.3), (-3.8, 2.0, 6.4), (-5.3, 0.4, 6.0), (-5.9, -1.4, 4.2), (-5.5, -2.8, 2.0),
               (-4.8, -3.6, 0.4)],
     (1.8, 1.05), (1.1, 0.65), (0.55,)),
]
PINCH = 0.1
# The fangs: (u, y, z) of their roots and tips, their roots' radius.
FANGS = [((-2.0, -4.4, 2.2), (-2.05, -6.35, 0.9), 0.55)]
# The shutters per frame: how far in from the slot's sides they reach (u of their inner edges; None: open).
FRAMES = [("tan_crab", 267, None, 0x7c, 0x79), ("tan_crab_269", 269, 1.5, 0x79, 0x77),
          ("tan_crab_271", 271, 0.5, 0x77, 0x77)]
SHUTTER = (0.22, 0.2)      # their thickness and their edges' rounding

# The tans and greys by the light a face gets (how far it faces up and the sun, the faces towards the sun shining).
TAN = ((0.3, 0.5, 0.74), (0x15, 0x17, 0x1a, 0x1c))
GREY = ((0.45, 0.75), (0x06, 0x09, 0x0c))
REDS = {0x71: 0.25, 0x74: 0.33, 0x77: 0.42, 0x79: 0.5, 0x7c: 0.58}


def materials():
    m = {}
    for index in TAN[1]:
        m[index] = k.material(f"crab_tan_{index:x}", palette=index, metallic=0.1, roughness=0.5 if index < 0x18 else 0.4)
    for index in GREY[1]:
        m[index] = k.material(f"crab_grey_{index:x}", palette=index, metallic=0.1, roughness=0.32)
    m["dark"] = k.material("crab_dark", palette=0x02, metallic=0.3, roughness=0.45)
    glow = k.level_palette()
    for index, strength in REDS.items():
        m[index] = k.material(f"crab_red_{index:x}", palette=index, metallic=0.0, roughness=0.3, emission=glow[index],
                              emission_strength=strength)
    return m


def light(n):
    sun = max(0.0, n.dot(SUN))
    return 0.6 * n.z + 0.3 * sun + 0.1 * sun ** 6


def band(levels, value):
    return levels[1][sum(value > b for b in levels[0])]


def interp(points, t):
    if t <= points[0][0]:
        return points[0][1]
    for (t0, v0), (t1, v1) in zip(points, points[1:]):
        if t <= t1:
            return v0 + (v1 - v0) * (t - t0) / (t1 - t0)
    return points[-1][1]


def paint_bands(obj, fields, paint):
    """Cuts obj's faces along the contours of fields [(field(co, normal), threshold)] so that colours change along
    smooth lines, then gives each face the material paint(centre, normal) returns."""
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    for field, threshold in fields:
        bmesh.ops.triangulate(bm, faces=bm.faces[:])   # (a contour crosses a triangle at most once)
        bm.normal_update()
        values = {v: field(v.co, v.normal) for v in bm.verts}
        split_along(bm, values, threshold)
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    bm.normal_update()
    mats = []
    keys = []
    for f in bm.faces:
        # (the corners' normals averaged, as the contours were drawn from them: the colours meet along the cuts)
        n = sum((v.normal for v in f.verts), Vector()).normalized()
        mat = paint(f.calc_center_median(), n)
        if mat not in mats:
            mats.append(mat)
        keys.append(mats.index(mat))
    for f, i in zip(bm.faces, keys):
        f.material_index = i
    obj.data.materials.clear()   # (before the faces are written back: clearing the slots resets their indices)
    for mat in mats:
        obj.data.materials.append(mat)
    bm.to_mesh(obj.data)
    bm.free()
    return obj


def icosphere(name, centre, radii, subdivisions):
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=subdivisions, radius=1.0)
    for v in bm.verts:
        d = v.co.normalized()
        v.co = Vector((centre.x + d.x * radii.x, centre.y + d.y * radii.y, centre.z + d.z * radii.z))
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    return obj


def top_of(ellipsoid, u, y):
    """The ellipsoid's top at (u, y), or None outside it."""
    c, r = ellipsoid
    q = 1.0 - ((u - c.x) / r.x) ** 2 - ((y - c.y) / r.y) ** 2
    return c.z + r.z * math.sqrt(q) if q > 0 else None


# --- The head and the back ------------------------------------------------------------------------------------------

def slot_inside(u, y):
    """How far inside the slot (u, y) lies (pixels; negative outside), as the sprite draws it from above."""
    half, top, bottom = SLOT
    return min(half - abs(u), top - y, y - bottom)


def slot_ring(u, y):
    """How far out from the slot's hot middle (u, y) lies, a fraction of its half-sizes."""
    half, top, bottom = SLOT
    return math.hypot((u - SLOT_HOT[0]) / half, (y - SLOT_HOT[1]) / ((top - bottom) / 2))


def head(m, slot_mid, slot_side):
    c, r = HEAD
    obj = icosphere("head", c, r, 4)
    for v in obj.data.vertices:
        p = v.co
        rel = p - c
        n = Vector((rel.x / r.x ** 2, rel.y / r.y ** 2, rel.z / r.z ** 2)).normalized()
        if n.z > -0.2:
            sink = SLOT_DEPTH * smoothstep(-0.05, SLOT_ROUND, slot_inside(p.x, p.y))
            v.co = p - n * sink
    bm = bmesh.new()   # its underside (inside the belly, never seen) left out
    bm.from_mesh(obj.data)
    bmesh.ops.delete(bm, geom=[f for f in bm.faces if all(v.co.z < c.z - 0.62 * r.z for v in f.verts)], context="FACES")
    bm.to_mesh(obj.data)
    bm.free()

    def paint(cc, n):
        if slot_inside(cc.x, cc.y) > 0.0 and n.z > -0.3:
            s = slot_ring(cc.x, cc.y)
            return m[slot_mid if s < SLOT_RINGS[0] else slot_side if s < SLOT_RINGS[1] else
                     0x74 if s < SLOT_RINGS[2] else 0x71]
        return m[band(GREY, light(n))]

    fields = [(lambda co, n: slot_inside(co.x, co.y), 0.0)]
    fields += [(lambda co, n, r=r: slot_ring(co.x, co.y) - r if slot_inside(co.x, co.y) > -0.3 else 9.0, 0.0)
               for r in SLOT_RINGS]
    fields += [(lambda co, n, b=b: light(n) - b, 0.0) for b in GREY[0]]
    paint_bands(obj, fields, paint)
    return k.smooth(obj, 50)


def back(m):
    c, r = BACK
    obj = icosphere("back", c, r, 3)
    for v in obj.data.vertices:
        v.co.z = max(v.co.z, c.z - 0.7 * r.z)
    obj.data.materials.append(m["dark"])
    k.smooth(obj, 60)
    c, r = BELLY
    belly = icosphere("belly", c, r, 3)
    belly.data.materials.append(m["dark"])
    return obj, k.smooth(belly, 60)


def body_top(u, y):
    z = [t for t in (top_of(HEAD, u, y), top_of(BACK, u, y)) if t is not None]
    return max(z) if z else 3.0


# --- The crest ----------------------------------------------------------------------------------------------------

def crest(m):
    """The fin along the tops of the head and the back, its top glowing in segments, flaring into the cap."""
    half, height = FIN
    rings = []
    steps = 14
    for i in range(steps + 1):
        y = FIN_Y[0] + (FIN_Y[1] - FIN_Y[0]) * i / steps
        base = body_top(0.0, y) - 0.5
        w = half * (0.7 + 0.3 * smoothstep(FIN_Y[0], FIN_Y[0] + 1.5, y))
        ring = []
        for j in range(10):
            a = math.pi * j / 9
            ring.append(Vector((-w * math.cos(a), y, base + (height + 0.5) * max(0.0, math.sin(a)) ** 0.8)))
        ring += [Vector((w * 0.9, y, base - 0.4)), Vector((-w * 0.9, y, base - 0.4))]
        rings.append(ring)
    fin = k.loft("fin", rings, m[0x74])
    k.recalc_normals(fin)
    cap = icosphere("cap", CAP[0], CAP[1], 3)
    for v in cap.data.vertices:
        v.co.z = max(v.co.z, CAP[0].z - 0.6 * CAP[1].z)

    def fin_paint(cc, n):
        if n.z > 0.55:
            heat = interp(FIN_HEAT, cc.y)
            return m[0x7c] if heat > 10 else m[0x77] if heat > 6.5 else m[0x74] if heat > 3.5 else m[0x71]
        return m[0x71] if n.z < 0.0 else m[0x74]

    fields = [(lambda co, n: n.z - 0.55, 0.0)] + [(lambda co, n, h=h: interp(FIN_HEAT, co.y) - h, 0.0)
                                                   for h in (3.5, 6.5, 10.0)]
    paint_bands(fin, fields, fin_paint)
    k.smooth(fin, 60)

    hot, radius = CAP_HOT

    def cap_paint(cc, n):
        d = (Vector((cc.x, cc.y)) - hot).length
        if n.z < 0.15:
            return m[0x71]
        return m[0x7c] if d < radius else m[0x77] if d < 2.0 * radius + 0.4 else m[0x74]

    paint_bands(cap, [(lambda co, n: n.z - 0.15, 0.0), (lambda co, n: (Vector((co.x, co.y)) - hot).length - radius, 0.0),
                      (lambda co, n: (Vector((co.x, co.y)) - hot).length - 2.0 * radius - 0.4, 0.0)], cap_paint)
    k.smooth(cap, 60)
    return fin, cap


# --- The legs and the fangs -------------------------------------------------------------------------------------

def chaikin_open(points, iterations=3):
    pts = [Vector(p) for p in points]
    for _ in range(iterations):
        out = [pts[0]]
        for a, b in zip(pts, pts[1:]):
            out += [a.lerp(b, 0.25), a.lerp(b, 0.75)]
        out.append(pts[-1])
        pts = out
    return pts


def oval_tube(name, path, sections, mat, around=12):
    """A tube along the path with an oval section (half-widths (across, other) per point): across is horizontal,
    square to the path (so the leg is broad seen from above, whether it reaches out or hangs down), the other way
    square to both; closed at both ends."""
    n = len(path)
    tangents = [(path[min(i + 1, n - 1)] - path[max(i - 1, 0)]).normalized() for i in range(n)]
    rings = []
    previous = None
    for i in range(n):
        t = tangents[i]
        side = Vector((-t.y, t.x, 0.0)).normalized()
        other = t.cross(side).normalized()
        if (previous is None and other.z < 0) or (previous is not None and other.dot(previous) < 0):
            other = -other     # (kept turning the same way along the leg: no sudden twist)
        previous = other
        a, b = sections[i]
        rings.append([path[i] + side * (a * math.cos(2 * math.pi * j / around)) +
                      other * (b * math.sin(2 * math.pi * j / around)) for j in range(around)])
    obj = k.loft(name, rings, mat, start_point=path[0] - tangents[0] * 0.2, end_point=path[-1] + tangents[-1] * 0.3)
    k.recalc_normals(obj)
    return obj


def resample(path, count):
    """count points along the path, evenly spaced along its length."""
    lengths = [0.0]
    for a, b in zip(path, path[1:]):
        lengths.append(lengths[-1] + (b - a).length)
    out = []
    j = 0
    for i in range(count):
        s = lengths[-1] * i / (count - 1)
        while j < len(path) - 2 and lengths[j + 1] < s:
            j += 1
        t = (s - lengths[j]) / max(1e-9, lengths[j + 1] - lengths[j])
        out.append(path[j].lerp(path[j + 1], min(1.0, max(0.0, t))))
    return out


def leg(m, name, points, root, tip, joints, side):
    path = resample(chaikin_open([(side * -u, y, z) for u, y, z in points], 3), 3 + 3 * len(points))
    lengths = [0.0]
    for a, b in zip(path, path[1:]):
        lengths.append(lengths[-1] + (b - a).length)
    total = lengths[-1]
    sections = []
    for s in lengths:
        t = s / total
        pinch = max(math.exp(-((t - j) / 0.035) ** 2) for j in joints)
        f = 1.0 - PINCH * pinch
        taper = smoothstep(0.0, 1.0, t) ** 1.3
        sections.append(((root[0] + (tip[0] - root[0]) * taper) * f, (root[1] + (tip[1] - root[1]) * taper) * f))
    obj = oval_tube(f"leg_{name}_{'l' if side < 0 else 'r'}", path, sections, m[TAN[1][2]])
    for v in obj.data.vertices:
        v.co.z = max(v.co.z, 0.0)
    k.smooth(obj, 70)
    paint_bands(obj, [(lambda co, n, b=b: light(n) - b, 0.0) for b in TAN[0]],
                lambda cc, n: m[band(TAN, light(n))])
    return k.smooth(obj, 70)


def fang(m, root, tip, radius, side):
    r0, t0 = Vector((side * -root[0], root[1], root[2])), Vector((side * -tip[0], tip[1], tip[2]))
    axis = t0 - r0
    profile = [(radius, 0.0), (radius * 0.9, 0.35), (radius * 0.55, 0.7), (0.06, 1.0)]
    rings = []
    ref = Vector((1.0, 0.0, 0.0))
    a = axis.normalized().cross(ref).normalized()
    b = axis.normalized().cross(a).normalized()
    for r, t in profile:
        p = r0 + axis * t
        rings.append([p + (a * math.cos(2 * math.pi * j / 10) + b * math.sin(2 * math.pi * j / 10)) * r
                      for j in range(10)])
    obj = k.loft(f"fang_{'l' if side < 0 else 'r'}", rings, m[GREY[1][2]], end_point=t0 + axis.normalized() * 0.05)
    k.recalc_normals(obj)
    mk.paint(obj, lambda cc, n: m[GREY[1][1]] if n.z < 0.2 else None)
    return k.smooth(obj, 50)


# --- The shutters -----------------------------------------------------------------------------------------------

def shutters(m, inner):
    """Two grey plates over the slot's sides, from its sides in to inner (u), lying on the head's front."""
    c, r = HEAD
    half, top, bottom = SLOT
    out = []
    for side in (-1.0, 1.0):
        u0, u1 = side * inner, side * (half + 0.15)
        cols, rows = 5, 7
        top_pts, low_pts = [], []
        for i in range(rows + 1):
            y = top + 0.12 - (top - bottom + 0.24) * i / rows
            trow, lrow = [], []
            for j in range(cols + 1):
                u = u0 + (u1 - u0) * j / cols
                rel = Vector((u - c.x, y - c.y, 0.0))
                q = 1.0 - (rel.x / r.x) ** 2 - (rel.y / r.y) ** 2
                z = c.z + r.z * math.sqrt(max(q, 0.0))
                rel.z = z - c.z
                n = Vector((rel.x / r.x ** 2, rel.y / r.y ** 2, rel.z / r.z ** 2)).normalized()
                edge = min(abs(u - u0), abs(u - u1), y - (bottom - 0.12), (top + 0.12) - y)
                lift = SHUTTER[0] * math.sqrt(max(0.0, min(1.0, edge / SHUTTER[1])))
                p = Vector((u, y, z)) + n * (0.04 + lift)
                trow.append(p)
                lrow.append(Vector((u, y, z)) - n * 0.25)
            top_pts.append(trow)
            low_pts.append(lrow)
        verts, faces = [], []
        for grid in (top_pts, low_pts):
            for row in grid:
                verts += [tuple(p) for p in row]
        w = cols + 1
        off = (rows + 1) * w
        for i in range(rows):
            for j in range(cols):
                a, b, cc, d = i * w + j, i * w + j + 1, (i + 1) * w + j + 1, (i + 1) * w + j
                faces.append((a, b, cc, d))
                faces.append((off + d, off + cc, off + b, off + a))
        # the rims joining the two sides
        ring = [(0, j) for j in range(cols + 1)] + [(i, cols) for i in range(1, rows + 1)] + \
               [(rows, j) for j in range(cols - 1, -1, -1)] + [(i, 0) for i in range(rows - 1, 0, -1)]
        for (i0, j0), (i1, j1) in zip(ring, ring[1:] + ring[:1]):
            a, b = i0 * w + j0, i1 * w + j1
            faces.append((b, a, off + a, off + b))
        obj = k.mesh_object(f"shutter_{'l' if side < 0 else 'r'}", verts, faces, m[GREY[1][2]])
        k.recalc_normals(obj)
        mk.paint(obj, lambda cc, n: m[GREY[1][2]] if n.z > 0.75 else m[GREY[1][1]] if n.z < 0.3 else None)
        out.append(k.smooth(obj, 40))
    return out


# --- The model ----------------------------------------------------------------------------------------------------

def build_model(name, inner, slot_mid, slot_side):
    k.reset()
    m = materials()
    head(m, slot_mid, slot_side)
    back(m)
    crest(m)
    for side in (-1.0, 1.0):
        for leg_name, points, root, tip, joints in LEGS:
            leg(m, leg_name, points, root, tip, joints, side)
        for root, tip, radius in FANGS:
            fang(m, root, tip, radius, side)
    if inner is not None:
        shutters(m, inner)
    parts = mk.meshes()
    mk.transform(parts, Matrix.Translation((AXIS_X, 0.0, 0.0)))
    return triangulate(parts)


def outline_ring(sheet, sprite):
    """The sprite's outline: its near-black pixels (0x01) next to a transparent one."""
    from sprite_profile import sprite_indices
    idx = sprite_indices(sheet, sprite)
    h, w = len(idx), len(idx[0])

    def empty(r, c):
        return not (0 <= r < h and 0 <= c < w) or idx[r][c] is None
    ring = [[idx[r][c] == 0x01 and any(empty(r + dr, c + dc) for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)))
             for c in range(w)] for r in range(h)]
    if sprite != 267:
        ring = [[False] + row[:-1] for row in ring]
    return ring


def compare_core(label, covered, mask, ring):
    """The overlap leaving the sprite's outline ring out (neither counted for nor against)."""
    h, w = len(mask), len(mask[0])
    both = sum(covered[y][x] and mask[y][x] and not ring[y][x] for y in range(h) for x in range(w))
    either = sum((covered[y][x] or mask[y][x]) and not ring[y][x] for y in range(h) for x in range(w))
    print("silhouette overlap %s without the sprite's outline: %.3f" % (label, both / max(either, 1)))


def mask_of(sheet, sprite):
    mask = k.sprite_mask(sheet, sprite)
    if sprite != 267:  # 269 and 271 are drawn a pixel to the left of 267
        mask = [[False] + row[:-1] for row in mask]
    return mask


def build():
    options = k.args()
    out = mk.outdir(options)
    only = set(options["only"].split(",")) if "only" in options else None
    for name, sprite, inner, slot_mid, slot_side in FRAMES:
        if only is not None and name not in only:
            continue
        parts = build_model(name, inner, slot_mid, slot_side)
        bpy.context.view_layer.update()
        if "check" in options:
            sheet = os.path.join(options["check"], "enemy_8.png")
            covered = mk.coverage(parts, 24, 28)
            mask = mask_of(sheet, sprite)
            mk.compare("%s (8 %d)" % (name, sprite), covered, mask)
            compare_core("%s (8 %d)" % (name, sprite), covered, mask, outline_ring(sheet, sprite))
        bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
        mk.report(name, parts, os.path.join(out, name + ".glb"))
        if "preview" in options:
            mk.preview(options["preview"] + name, parts)


if __name__ == "__main__":
    build()
