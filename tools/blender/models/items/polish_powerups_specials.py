"""The special weapons' pick-ups of the power-ups sheet ("twoplayer" in the catalogue, powerups in models.cfg):
sprites 271, 273, 275, 277, 121 and 123 (enemy types 829-834 of every episode, values 32101-32106: Repulsor, Pearl
Wind, Soul of Zinglon, Attractor, Ice Beam and Flare, the special weapon each gives; 2x2, 24 x 28 pixels; about 70 of
each in the levels, all left by destroyed enemies), and the dual MegaLaser's brown orb (sprite 3: episode 4's enemy
types 1121 and 1296, values 32115 and 32141 SDF Main Gun, set in ICESECRET's sky), polished (2026-10-21; it replaces
powerups_specials.py: powerups_parts.ship()'s generic dark jet with crude effects round it, and a panelled orb with
two bars). One frame each, not animated; no other enemy shows these sprites (catalog.json), and the sheet's other
fighter sprites (53, 55, 91, 93, 125-131, 279, 283: the other specials) are shown by no enemy.

How the game shows them: a drop worth more than 30000 is made in enemy slots 0-24 (tyrian2.c: enemy_offset = 0),
which are drawn in the sky-enemy phase (JE_drawEnemy(25); layer3d.c: 22 pixels plus the terrain's headroom over the
ground), centred in height there; ICESECRET's events put sprite 3 on the sky layer too. The power-ups keep still
(batch A's choice, so that their symbols stay as the sprites draw them: yaw=0, no spin), so these models keep the
sprite's place and picture; the fighter's centre line is the sprite's column 12 (x = 0.5), half a pixel off the
origin, should they ever turn (spin=).

The fighter. The six specials draw the same small fighter pixel for pixel (columns 6-18, rows 6-19; its outline index
0x30 in 271, 0xf0 in the others). As the sprites and their 4x upscales draw it: a crown of three blades. The spire
(the fuselage, columns 10-14 of rows 6-14): a pointed nose, a dark canopy (rows 10-11) with a glint before it (row 9),
red lights either side of its root (rows 13-14); the white engine block behind it (columns 11-13 of rows 15-17), the
red exhaust under it (row 18); two long curved side blades from their tips (columns 7 and 17 of row 12) down to the
base, their lit ridges running along their inner edges ((7, 13) (8, 14) (9, 15) (9, 16) and mirrored); dark gaps
between them and the block (columns 10 and 14 of rows 15-18); a dark base under it all (rows 15-19). Built as lofted
ridged blades (leaf(): cross-sections of an outer facet, a bright ridge line and an inner facet, between thin dark
lips, the sprite's outline, in its maroon 0xf2), smooth along them and sharp across their ridges: the spire, with a
long dark glass canopy (a cut lozenge) on its ridge and red glowing lozenges on its flanks; the blades (the right one
the left one mirrored); a box for the block (its top sloping back, its top edges chamfered, its top painted 0x0e) with
the exhaust glowing red at its back; a dark plate (0x04) under them, seen in the gaps. Silver in ramp 0 (0x0b, a
little metallic), lighter than the sprite's greys (they read darker in the game).

The effects, as the sprites draw them, and as built (each glowing in its own palette colours, 0.08-0.6):
- 271 Repulsor: steel-blue field strokes (ramp 3): two outer arcs round the fighter's upper half (columns 3-21, rows
  3-12: parts of a circle of radius 8.3 round (0.5, 1.7), 2.5-3 pixels thick, blunt at the top, pointed at the
  bottom), a thin streak inside each (rows 7-10), a U under the tail (rows 20-24) and a short ripple just under the
  tail (row 20). Bands of an elliptical cross-section along them (band()), their outer halves lighter, the streaks
  and the ripple lightest.
- 273 Pearl Wind: three icy pearls (ramp 8) flying up the screen, each a square on its corner 8 pixels across with a
  dark blue tail (ramp 3) falling 8-10 pixels below it; one picture at three places ((-8, 7), (7, 5), (-2, -6)), the
  fighter's right blade over the second pearl's tail, the third pearl over the fighter's lower left. Cushions of ice
  (superellipsoids turned 45 degrees, in four frost bands by their slope, lightest on top) set in teardrop wisps that
  bend a little at their ends, three shades from the pearl down; the fighter lies a pixel higher than the second
  pearl's tail and lower than the third pearl.
- 275 Soul of Zinglon: the fighter in a capsule (columns 6-18 of rows 0-27), its light gathering along its middle
  (0x33 at its outline to 0x3f, about a shade a pixel). A cradle, the capsule's lower half, its inside glowing in five
  bands by how far out they lie (seen from above: the sprite's even fall from the middle to the outline), its outside
  dark; the fighter lying in it; a glass lid over it (see-through: a dark rim, 0.55, clear on top, 0.1; the game draws
  it blended, in the order of its triangles, so they run from the bottom up).
- 277 Attractor: four needles from the corners in at the fighter (ramp 3, lighter towards their inner ends), their
  tips pink (ramp 4), pale blue, orange (ramp 7) and lavender (ramp 5), the upper right and lower left ones curving.
  Tapered tubes along the strokes, in three shades along them, a glowing cap on each.
- 121 Ice Beam: an icy burst over the nose (columns 9-15 of rows 0-4, lit at its upper right), two streams from it
  down either side of the nose (rows 4-11) and four sparkles. A cut ice gem (girdle, bezels, star facets, table:
  0x3b-0x3f) with four hexagonal shards growing out of it; two tapering streams, lighter along their upper parts;
  four-pointed sparkles (two crossed lozenges each).
- 123 Flare: a ring of fire in a shield's shape round the fighter (columns 3-21 of rows 3-23: a dark red outline 0x73,
  red 0x76, a hot yellow line 0x7a-0x7f inside), deep red (0x75) within it. A closed band whose cross-section is
  yellow towards the fighter, orange on top, red outside and dark red at the very outside, its height waving (the
  flames), matte (glossy waves glinted like a string of bulbs); a low plate of deep red under the fighter.
- 3 MegaLaser Dual: a tan orb (ramp 14, columns 2-22 of rows 3-23, a dark outline) with two glowing blue bars (ramp 9,
  columns 8-10 and 14-16 of rows 6-20, a pale line down each) in dark slots. A squashed sphere in five bands by its
  slope (lightest on top; a little emission in its own colours, so that the ball doesn't read black from the slanted
  camera), two rounded troughs cut into it (a stadium minus a smaller sphere: their floors follow the ball) and the
  bars lying in them along the ball's curve.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera; the origin is the
sprite's centre (pixel 12, 14): column c is x = c + 0.5 - 12, row r is y = 13.5 - r. Every model stands on z = 0 (the
game centres them in height anyway). Every mesh is triangulated before export (polish_k_pod.triangulate).

models.cfg: the model lines stay (model pu_repulsor items/pu_repulsor.glb and so on), so do the sprite lines (yaw=0;
glow=18:0.25 on 275, glow=20:0.35 on 123); the comment above them is rewritten.

Replaces powerups_specials.py (all of it: its seven models are these seven), powerups_parts.py's ship() (only
powerups_specials.py used it), RAMP_BROWN and orb()'s rim (only the brown orb used them), and powerups.py's import of
powerups_specials and its entry in the modules it builds.

Options after "--": --outdir <dir> (default assets/models/items), --check <sheets dir or powerups.png> (each model's
silhouette against its sprite; with Ice Beam also the fighter's own against its pixels), --preview <prefix>,
--only <name,...>.
"""
import math
import os
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector
from mathutils.geometry import delaunay_2d_cdt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polish_item_kit as kit  # noqa: E402
from polish_item_kit import k  # noqa: E402

AXIS = 0.5        # the fighter's centre line: column 12
FIGHTER = []      # the parts of the fighter of the model being built (for its own silhouette check)


# --- Materials -----------------------------------------------------------------------------------------------------

def glow_mat(name, index, emit, strength, metallic=0.2, roughness=0.25, alpha=None):
    """A palette material glowing in the colour of the palette index emit."""
    return k.material(name, palette=index, metallic=metallic, roughness=roughness, emission=k.level_palette()[emit],
                      emission_strength=strength, alpha=alpha)


# --- A solid over a plan -------------------------------------------------------------------------------------------

def resample(outline, step):
    """The closed outline with points every `step` along its edges (its own points kept)."""
    out = []
    n = len(outline)
    for i in range(n):
        (ax, ay), (bx, by) = outline[i], outline[(i + 1) % n]
        count = max(1, int(math.ceil(math.hypot(bx - ax, by - ay) / step)))
        for s in range(count):
            t = s / count
            out.append((ax + (bx - ax) * t, ay + (by - ay) * t))
    return out


def inside(p, outline):
    x, y = p
    result = False
    n = len(outline)
    for i in range(n):
        (ax, ay), (bx, by) = outline[i], outline[(i + 1) % n]
        if (ay > y) != (by > y) and x < ax + (y - ay) * (bx - ax) / (by - ay):
            result = not result
    return result


def edge_distance(p, outline):
    """The distance from p to the closed outline."""
    x, y = p
    best = 1e9
    n = len(outline)
    for i in range(n):
        (ax, ay), (bx, by) = outline[i], outline[(i + 1) % n]
        dx, dy = bx - ax, by - ay
        length2 = dx * dx + dy * dy
        t = 0.0 if length2 < 1e-12 else max(0.0, min(1.0, ((x - ax) * dx + (y - ay) * dy) / length2))
        best = min(best, math.hypot(x - ax - t * dx, y - ay - t * dy))
    return best


def area(loop):
    return sum(loop[i][0] * loop[(i + 1) % len(loop)][1] - loop[(i + 1) % len(loop)][0] * loop[i][1]
               for i in range(len(loop))) / 2


def rounded(d, radius):
    """A quarter circle's rise over `radius` in from an edge (0 at the edge, 1 past radius)."""
    t = max(0.0, min(1.0, d / radius))
    return math.sqrt(1.0 - (1.0 - t) ** 2)


def relief(name, outline, height, mat, step=0.8, edge_step=0.3, bottom=0.0):
    """A solid over a plan (outline counter-clockwise [(x, y)]): its top the surface z = height(x, y, d) (d the
    distance in from the outline), its walls straight down to z = bottom, its underside flat; triangulated evenly (a
    constrained Delaunay triangulation of the outline's points and a grid inside), so that its top shades smoothly."""
    ring = resample(outline, edge_step)
    points = [Vector(p) for p in ring]
    nb = len(points)
    xs, ys = [p[0] for p in ring], [p[1] for p in ring]
    row, y = 0, min(ys) + step * 0.5
    while y < max(ys):
        x = min(xs) + (step * 0.5 if row % 2 else 0.0)
        while x < max(xs):
            if inside((x, y), outline) and edge_distance((x, y), outline) > step * 0.45:
                points.append(Vector((x, y)))
            x += step
        y += step * 0.866
        row += 1
    edges = [(i, (i + 1) % nb) for i in range(nb)]
    verts2, _, faces, orig, _, _ = delaunay_2d_cdt(points, edges, [list(range(nb))], 1, 1e-6)
    bm = bmesh.new()
    top = [bm.verts.new((v.x, v.y, height(v.x, v.y, edge_distance((v.x, v.y), outline)))) for v in verts2]
    boundary = [None] * nb    # which output vertex each outline point became
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
    obj = kit.from_bmesh(name, bm, mat)
    return k.smooth(obj, 50)


# --- Convex parts (cut from planes, flat facets) -------------------------------------------------------------------

def plan_planes(poly, key, z=0.0, lean=None):
    """The half-spaces along a convex plan's edges (poly counter-clockwise [(x, y)]): upright walls, or with lean
    (rise per unit inwards) planes leaning in from the plan's edges at height z (a bevel round the top)."""
    out = []
    n = len(poly)
    for i in range(n):
        (ax, ay), (bx, by) = poly[i], poly[(i + 1) % n]
        nx, ny = by - ay, -(bx - ax)
        length = math.hypot(nx, ny)
        nx, ny = nx / length, ny / length
        normal = (nx, ny, 0.0) if lean is None else (nx * lean, ny * lean, 1.0)
        out.append((kit.general(normal, (ax, ay, z)), key))
    return out


def solid(name, pairs, mats):
    """A convex solid from (half-space, part key) pairs; mats: each key's material ("*": the rest)."""
    obj = kit.solid(name, [p for p, _ in pairs], [key for _, key in pairs], mats)
    kit.drop_parts(obj)
    return obj


def lozenge(name, length, width, height, mat):
    """A small cut jewel lying along y: a diamond in plan (half-length, half-width), its top a low pyramid."""
    plan = [(0, -length), (width, 0), (0, length), (-width, 0)]
    pairs = plan_planes(plan, "*") + plan_planes(plan, "*", 0.0, height / width * 0.8)
    pairs.append((kit.flat(-0.3, below=True), "*"))
    return solid(name, pairs, {"*": mat})


# --- Ridged blades -------------------------------------------------------------------------------------------------

def leaf(name, sections, tip, mats, z0=0.0, lip=(0.28, 0.32), ridge_w=0.14):
    """A blade lofted through cross-sections from its root to its tip: each section (outer edge (x, y), ridge
    (x, y), inner edge (x, y), the outer edge's height, the ridge's, the inner edge's), its walls standing from z0,
    a narrow lip round its top edges (lip: how far in, how high) and a bright strip ridge_w wide along its ridge; the
    sections meet in the point tip (x, y, z). mats: "edge" (walls, lips, root and underside), "*" (the facets),
    "ridge"."""
    bm = bmesh.new()
    rings = []
    lw, lh = lip
    for (o, r, i, zo, zr, zi) in sections:
        o, r, i = Vector((*o, 0)), Vector((*r, 0)), Vector((*i, 0))
        to_o = (o - r).normalized() if (o - r).length > 1e-6 else Vector((0, 0, 0))
        to_i = (i - r).normalized() if (i - r).length > 1e-6 else Vector((0, 0, 0))
        wo, wi = min(lw, (o - r).length * 0.4), min(lw, (i - r).length * 0.4)
        pts = [(o.x, o.y, z0), (o.x, o.y, zo), (o.x - to_o.x * wo, o.y - to_o.y * wo, zo + lh),
               (r.x + to_o.x * ridge_w, r.y + to_o.y * ridge_w, zr),
               (r.x + to_i.x * ridge_w, r.y + to_i.y * ridge_w, zr),
               (i.x - to_i.x * wi, i.y - to_i.y * wi, zi + lh), (i.x, i.y, zi), (i.x, i.y, z0)]
        rings.append([bm.verts.new(p) for p in pts])
    keys = ["edge", "edge", "*", "ridge", "*", "edge", "edge", "edge"]   # the faces from point j to j + 1
    order = sorted(mats)
    for a, b in zip(rings, rings[1:]):
        for j in range(8):
            f = bm.faces.new((a[j], a[(j + 1) % 8], b[(j + 1) % 8], b[j]))
            f.material_index = order.index(keys[j])
    apex = bm.verts.new(tip)
    for j in range(8):
        f = bm.faces.new((rings[-1][j], rings[-1][(j + 1) % 8], apex))
        f.material_index = order.index(keys[j])
    f = bm.faces.new(list(reversed(rings[0])))
    f.material_index = order.index("edge")
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=1e-5)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    obj = kit.from_bmesh(name, bm)
    for key in order:
        obj.data.materials.append(mats[key])
    return k.smooth(obj, 30)


def mirror_object(obj, name):
    """A copy mirrored across the fighter's centre line."""
    copy = obj.copy()
    copy.data = obj.data.copy()
    copy.name = name
    bpy.context.scene.collection.objects.link(copy)
    copy.data.transform(Matrix.Translation((AXIS, 0, 0)) @ Matrix.Scale(-1, 4, (1, 0, 0)) @
                        Matrix.Translation((-AXIS, 0, 0)))
    copy.data.flip_normals()
    return copy


# --- Bands along paths ---------------------------------------------------------------------------------------------

def catmull(points, samples=6):
    """A smooth path (Catmull-Rom) through the points (x, y, z), `samples` steps between each two."""
    pts = [Vector(q) for q in points]
    out = []
    for i in range(len(pts) - 1):
        p0, p1, p2 = pts[max(i - 1, 0)], pts[i], pts[i + 1]
        p3 = pts[min(i + 2, len(pts) - 1)]
        for j in range(samples):
            t = j / samples
            t2, t3 = t * t, t * t * t
            out.append(0.5 * (2 * p1 + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 +
                              (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
    out.append(pts[-1])
    return out


def arc(centre, radius, a0, a1, z, count):
    """Points along a circle's arc (angles in degrees, from a0 to a1) at height z."""
    cx, cy = centre
    return [Vector((cx + radius * math.cos(math.radians(a0 + (a1 - a0) * i / (count - 1))),
                    cy + radius * math.sin(math.radians(a0 + (a1 - a0) * i / (count - 1))), z))
            for i in range(count)]


def band(name, path, widths, heights, mats, pick=None, segments=12, closed=False):
    """A tube along the path (points (x, y, z)) with an elliptical cross-section: widths[i] across the path
    (level), heights[i] up; closed in a point where a width is 0 (pointed ends). pick(t, a) gives a face's material
    key from how far along the path it is (0-1) and its angle round the cross-section (0 the path's left side seen
    from above, 90 its top, 180 its right side)."""
    pts = [Vector(q) for q in path]
    n = len(pts)
    bm = bmesh.new()
    rings = []
    for i, p in enumerate(pts):
        t = (pts[(i + 1) % n] - pts[i - 1]) if closed else (pts[min(i + 1, n - 1)] - pts[max(i - 1, 0)])
        t.normalize()
        side = Vector((0, 0, 1)).cross(t)
        side = side.normalized() if side.length > 1e-6 else Vector((1, 0, 0))
        up = t.cross(side).normalized()
        w, h = widths[i], heights[i]
        if w < 1e-4:
            rings.append([bm.verts.new(p)])
            continue
        rings.append([bm.verts.new(p + side * (w * math.cos(2 * math.pi * j / segments)) +
                                   up * (h * math.sin(2 * math.pi * j / segments))) for j in range(segments)])
    order = sorted(mats)
    count = n if closed else n - 1
    for i in range(count):
        a, b = rings[i], rings[(i + 1) % n]
        tm = (i + 0.5) / count
        if len(a) == 1 and len(b) == 1:
            continue
        for j in range(segments):
            key = pick(tm, 360.0 * (j + 0.5) / segments) if pick else "*"
            if len(a) == 1:
                f = bm.faces.new((a[0], b[(j + 1) % segments], b[j]))
            elif len(b) == 1:
                f = bm.faces.new((a[j], a[(j + 1) % segments], b[0]))
            else:
                f = bm.faces.new((a[j], a[(j + 1) % segments], b[(j + 1) % segments], b[j]))
            f.material_index = order.index(key)
    if not closed:
        for ring, tm in ((rings[0], 0.0), (rings[-1], 1.0)):
            if len(ring) > 1:
                f = bm.faces.new(ring if ring is rings[-1] else list(reversed(ring)))
                f.material_index = order.index(pick(tm, 90.0) if pick else "*")
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    obj = kit.from_bmesh(name, bm)
    for key in order:
        obj.data.materials.append(mats[key])
    return k.smooth(obj, 70)


def taper(n, ends=(0.0, 0.0), power=0.6):
    """Widths along a path of n points: 1 in the middle, falling to ends[0] and ends[1] at its ends."""
    out = []
    for i in range(n):
        t = i / (n - 1)
        lo = ends[0] if t < 0.5 else ends[1]
        out.append(lo + (1 - lo) * math.sin(math.pi * t) ** power)
    return out


def profile_at(prof, t):
    """A profile [(t, value), ...] read at t (linear between its points)."""
    for (t0, v0), (t1, v1) in zip(prof, prof[1:]):
        if t <= t1 + 1e-9:
            return v0 + (v1 - v0) * (t - t0) / (t1 - t0)
    return prof[-1][1]


def banded_by_normal(bm, borders):
    """Cuts a bmesh's faces along the contours where its normals' z crosses the borders (smooth colour borders)
    and gives each face's band (how many borders its middle's normal is over)."""
    bm.normal_update()
    for t in borders:
        kit.split_along(bm, {v: v.normal.z for v in bm.verts}, t)
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    bm.normal_update()
    return [sum((sum(v.normal.z for v in f.verts) / len(f.verts)) > t for t in borders) for f in bm.faces]


# --- The fighter ---------------------------------------------------------------------------------------------------

# The spire (the nose, rows 6-14): sections from its root (where it meets the engine block) to its tip: y, half-width,
# its edges' height, its ridge's.
SPIRE = [(-1.15, 2.15, 1.45, 2.95), (0.5, 2.15, 1.5, 3.05), (3.6, 2.15, 1.45, 3.0), (4.35, 2.05, 1.35, 2.9),
         (5.05, 1.6, 1.15, 2.55), (5.9, 1.3, 1.0, 2.2), (6.7, 1.1, 0.85, 1.85), (7.55, 0.5, 0.75, 1.45)]
SPIRE_TIP = (8.15, 1.15)
# The left blade (the right one its mirror image): sections from its root at the bottom (row 19) up to its tip
# (row 12): outer edge, ridge (the lit pixels (7, 13), (8, 14), (9, 15), (9, 16)), inner edge, and the heights of the
# outer edge, the ridge and the inner edge.
BLADE = [((-2.95, -5.25), (-2.5, -5.1), (-1.95, -5.0), 0.55, 1.35, 1.0),
         ((-3.75, -4.3), (-2.5, -4.2), (-1.95, -4.2), 0.6, 1.75, 1.25),
         ((-4.0, -3.4), (-2.5, -3.3), (-1.95, -3.3), 0.6, 1.9, 1.35),
         ((-4.95, -2.55), (-2.5, -2.4), (-1.95, -2.4), 0.6, 2.0, 1.35),
         ((-5.95, -1.6), (-2.55, -1.5), (-1.95, -1.55), 0.6, 2.0, 1.35),
         ((-6.05, -0.6), (-3.4, -0.5), (-2.15, -0.5), 0.6, 1.85, 1.25),
         ((-6.0, 0.35), (-4.35, 0.45), (-3.25, 0.45), 0.6, 1.6, 1.1),
         ((-5.55, 1.3), (-4.6, 1.3), (-3.9, 1.3), 0.6, 1.3, 0.95)]
BLADE_TIP = (-4.55, 2.08, 0.95)
# The base plate under them (right halves, (dx, y) from the centre line, counter-clockwise from the centre line's
# lower end; in two parts, rows 15-16 being wider than rows 17-19), its height.
BASE_FRONT = [(0.0, -3.1), (4.6, -3.1), (5.55, -2.5), (6.1, -1.9), (6.15, -0.9), (5.6, -0.3), (0.0, -0.3)]
BASE_REAR = [(0.0, -6.12), (2.2, -6.08), (3.25, -5.8), (3.95, -5.25), (4.5, -4.55), (4.6, -3.0), (0.0, -3.0)]
BASE_Z = 0.75
# The engine block (rows 15-18): half-width, y from and to, its top's height at its front and back, its chamfer.
BLOCK = (1.45, -4.3, -0.7, 2.85, 2.5, 0.35)
# The canopy (dark glass on the ridge: y, half-length, half-width, height over the ridge), the red lights on the
# spire's sides (dx, y, half-length, half-width, height), the exhaust at the block's back (y, semi-axes, z).
CANOPY = (2.75, 1.45, 0.58, 0.38)
LIGHTS = (1.1, -0.05, 1.0, 0.5, 0.28)
EXHAUST = (-4.45, (1.15, 0.48, 0.6), 1.6)


def fighter_materials():
    pal = k.level_palette()
    return {
        "hull": k.material("fighter_hull", palette=0x0b, metallic=0.3, roughness=0.32),
        "bright": k.material("fighter_bright", palette=0x0e, metallic=0.25, roughness=0.28),
        "edge": k.material("fighter_edge", palette=0xf2, metallic=0.2, roughness=0.5),
        "base": k.material("fighter_base", palette=0x04, metallic=0.3, roughness=0.5),
        "canopy": k.material("fighter_canopy", palette=0x02, metallic=0.3, roughness=0.06),
        "red": k.material("fighter_red", palette=0x75, roughness=0.3, emission=pal[0x77], emission_strength=0.45),
        "exhaust": k.material("fighter_exhaust", palette=0x75, roughness=0.3, emission=pal[0x78],
                              emission_strength=0.55),
    }


def full(right):
    """A whole plan from its right half (counter-clockwise from the centre line's lower end to its upper end)."""
    left = [(-dx, y) for dx, y in reversed(right) if abs(dx) > 1e-9]
    return [(AXIS + dx, y) for dx, y in right + left]


def fighter(z=0.0):
    """The small fighter (columns 6-18, rows 6-19 of the sprites), its underside at z."""
    m = fighter_materials()
    mats = {"*": m["hull"], "edge": m["edge"], "ridge": m["bright"]}
    parts = []
    sections = [((AXIS - w, y), (AXIS, y), (AXIS + w, y), z + ze, z + zr, z + ze) for y, w, ze, zr in SPIRE]
    parts.append(leaf("spire", sections, (AXIS, SPIRE_TIP[0], z + SPIRE_TIP[1]), mats, z0=z + 0.2))
    sections = [(o, r, i, z + zo, z + zr, z + zi) for o, r, i, zo, zr, zi in BLADE]
    left = leaf("blade_left", sections, (BLADE_TIP[0], BLADE_TIP[1], z + BLADE_TIP[2]), mats, z0=z + 0.1)
    parts += [left, mirror_object(left, "blade_right")]
    # The base plate, dark, seen between the blades and the block.
    for name, half in (("base_front", BASE_FRONT), ("base_rear", BASE_REAR)):
        plan = full(half)
        pairs = plan_planes(plan, "*") + plan_planes(plan, "*", z + 0.3, 2.5)
        pairs += [(kit.flat(z + BASE_Z), "*"), (kit.flat(z, below=True), "*")]
        parts.append(solid(name, pairs, {"*": m["base"]}))
    # The engine block: a box, its top sloping to the back, its top edges chamfered.
    hw, by0, by1, hf, hb, ch = BLOCK
    walls = plan_planes([(AXIS - hw, by0), (AXIS + hw, by0), (AXIS + hw, by1), (AXIS - hw, by1)], "*")
    top = (kit.general((0.0, -(hf - hb) / (by1 - by0), 1.0), (AXIS, by1, z + hf)), "block")
    pairs = walls + [top] + [(kit.chamfer(w, top[0], ch), "*") for w, _ in walls]
    pairs.append((kit.flat(z + 0.6, below=True), "*"))
    parts.append(solid("block", pairs, {"*": m["hull"], "block": m["bright"]}))
    # The canopy: a long dark jewel on the ridge.
    cy, cl, cw, chh = CANOPY
    canopy = lozenge("canopy", cl, cw, chh + 0.6, m["canopy"])
    canopy.data.transform(Matrix.Translation((AXIS, cy, z + 2.75)))
    parts.append(canopy)
    # The red lights on the spire's sides, lying on its facets.
    ldx, ly, ll, lw, lh = LIGHTS
    slope = (2.95 - 1.45) / 2.15
    for s in (1, -1):
        light = lozenge("light", ll, lw, lh, m["red"])
        light.data.transform(Matrix.Translation((AXIS + s * ldx, ly, z + 2.95 - slope * ldx - 0.06))
                             @ Matrix.Rotation(-s * math.atan(slope), 4, "Y"))
        parts.append(light)
    ey, radii, ez = EXHAUST
    parts.append(k.smooth(k.ellipsoid("exhaust", (AXIS, ey, z + ez), radii, m["exhaust"], 14, 8), 70))
    FIGHTER[:] = parts
    return list(parts)


def is_fighter(index):
    """The fighter's own pixels: its greys (ramp 0), its reds (ramp 7) and its outline (0xf0)."""
    return index == 0xf0 or index < 16 or 0x70 <= index <= 0x7f


# --- 271: Repulsor -------------------------------------------------------------------------------------------------

# Its field: two outer arcs (a circle round FIELD_C, radius FIELD_R, from FIELD_A degrees round to the left, the right
# one mirrored; half-width FIELD_W at the top growing to FIELD_W2 at the bottom, as the sprite's strokes), a streak
# inside each (through INNER), the U under the tail (through BOWL) and a short ripple just under the tail (RIPPLE:
# centre, radius, angles); their half-widths and the height they float at.
FIELD_C, FIELD_R, FIELD_A = (AXIS, 1.7), 8.3, (101.0, 182.0)
FIELD_W, FIELD_W2 = 1.25, 1.45
INNER = [(-2.3, 6.8), (-3.3, 5.6), (-3.65, 4.5), (-4.6, 3.25)]
BOWL = [(-4.0, -6.85), (-3.2, -7.85), (-1.95, -8.95), (-0.45, -9.8), (1.45, -9.8), (2.95, -8.95), (4.2, -7.85),
        (5.0, -6.85)]
RIPPLE = ((AXIS, -2.0), 4.5, (248.0, 292.0))
INNER_W, BOWL_W, RIPPLE_W, FIELD_Z = 0.42, 0.98, 0.45, 1.6


def field_piece(name, path, widths, mats, outer=None):
    """A band of the field along a path, its outer half (outer: the path's "left" or "right") lighter; without
    outer, a streak in the lightest colour."""
    heights = [0.55 * v for v in widths]
    if outer is None:
        return band(name, path, widths, heights, {"*": mats["spark"]})

    def pick(t, a):
        return "out" if (100.0 < a < 260.0) == (outer == "right") else "*"
    return band(name, path, widths, heights, {"*": mats["*"], "out": mats["out"]}, pick)


def repulsor():
    parts = fighter()
    mats = {"*": glow_mat("field", 0x36, 0x38, 0.35, 0.35), "out": glow_mat("field_out", 0x3a, 0x3b, 0.42, 0.35),
            "spark": glow_mat("field_spark", 0x3c, 0x3d, 0.55)}
    a0, a1 = FIELD_A
    count = 30
    widths = [(FIELD_W + (FIELD_W2 - FIELD_W) * i / (count - 1)) * v
              for i, v in enumerate(taper(count, (0.8, 0.0), 0.3))]
    # Counter-clockwise on the left (its outer side the path's right), clockwise on the right.
    parts.append(field_piece("field_left", arc(FIELD_C, FIELD_R, a0, a1, FIELD_Z, count), widths, mats, "right"))
    parts.append(field_piece("field_right", arc(FIELD_C, FIELD_R, 180.0 - a0, 180.0 - a1, FIELD_Z, count), widths,
                             mats, "left"))
    for side, sx in (("left", 1), ("right", -1)):
        path = catmull([(AXIS + sx * (x - AXIS), y, FIELD_Z) for x, y in INNER], 4)
        parts.append(field_piece("inner_" + side, path, [INNER_W * v for v in taper(len(path), (0.0, 0.0), 0.5)],
                                 mats))
    path = catmull([(x, y, FIELD_Z - 0.2) for x, y in BOWL], 5)
    parts.append(field_piece("bowl", path, [BOWL_W * v for v in taper(len(path), (0.75, 0.75), 0.3)], mats, "right"))
    c, r, (r0, r1) = RIPPLE
    parts.append(field_piece("ripple", arc(c, r, r0, r1, FIELD_Z, 12), [RIPPLE_W * v for v in taper(12, (0, 0), 0.5)],
                             mats))
    return parts


# --- 273: Pearl Wind -----------------------------------------------------------------------------------------------

# The three pearls: (x, y, z of the middle, the tail's length, how far its end bends to the right); each a cushion of
# ice (a superellipsoid turned 45 degrees, a square on its corner as the sprite draws it: PEARL half-side, POWER, its
# half-height and the power of its height); the fighter's height between the second pearl's tail and the third pearl.
PEARLS = [(-8.0, 7.0, 3.1, 9.6, 0.55), (7.0, 5.0, 2.25, 9.6, 0.5), (-2.0, -6.0, 4.4, 7.9, -0.5)]
PEARL_FIGHTER_Z = 1.65
PEARL, POWER, PEARL_Z, PEARL_POWER_Z = 3.05, 3.3, 2.2, 2.2
# The pearls' frost: bands by the surface's slope (the normal's z), from the rim to the top: (lower border, palette
# index, glowing in, glow).
PEARL_BANDS = [(-1.0, 0x84, 0x86, 0.24), (0.25, 0x8a, 0x8b, 0.3), (0.62, 0x8c, 0x8d, 0.36), (0.9, 0x8e, 0x8e, 0.4)]
# The tails: half-widths along them (from the pearl's middle, as fractions of the length), how flat they are, how
# far under the pearl's middle they lie, and their shades from the pearl down (from where, palette index, glowing in,
# glow).
TAIL = [(0.0, 3.0), (0.07, 3.7), (0.2, 3.55), (0.4, 2.7), (0.6, 1.8), (0.8, 0.95), (0.93, 0.4), (1.0, 0.0)]
TAIL_SQUASH, TAIL_DROP = 0.42, 0.6
TAIL_SHADES = [(0.0, 0x39, 0x3a, 0.42), (0.36, 0x37, 0x38, 0.34), (0.66, 0x35, 0x36, 0.28)]


def superellipsoid(name, centre, mats, segments=36, rings=18, turn=45.0):
    """A pearl: |u/a|^p + |v/a|^p + |z/c|^q = 1 in axes turned `turn` degrees (a = PEARL, p = POWER, c = PEARL_Z,
    q = PEARL_POWER_Z), painted in PEARL_BANDS by its normal's z (mats: one material per band)."""
    cx, cy, cz = centre
    a, p, c, q = PEARL, POWER, PEARL_Z, PEARL_POWER_Z
    tr = math.radians(turn)
    bm = bmesh.new()

    def point(theta, phi):
        ct, st, cp, sp = math.cos(theta), math.sin(theta), math.cos(phi), math.sin(phi)
        r = abs(sp) ** (2 / q)
        u = a * r * math.copysign(abs(ct) ** (2 / p), ct)
        v = a * r * math.copysign(abs(st) ** (2 / p), st)
        return (cx + u * math.cos(tr) - v * math.sin(tr), cy + u * math.sin(tr) + v * math.cos(tr),
                cz + c * math.copysign(abs(cp) ** (2 / q), cp))

    top = bm.verts.new((cx, cy, cz + c))
    grid = [[bm.verts.new(point(2 * math.pi * j / segments, math.pi * i / rings)) for j in range(segments)]
            for i in range(1, rings)]
    bottom = bm.verts.new((cx, cy, cz - c))
    for j in range(segments):
        bm.faces.new((top, grid[0][j], grid[0][(j + 1) % segments]))
        bm.faces.new((grid[-1][(j + 1) % segments], grid[-1][j], bottom))
    for i in range(len(grid) - 1):
        for j in range(segments):
            bm.faces.new((grid[i][j], grid[i + 1][j], grid[i + 1][(j + 1) % segments], grid[i][(j + 1) % segments]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    keys = banded_by_normal(bm, [b[0] for b in PEARL_BANDS[1:]])
    obj = kit.from_bmesh(name, bm)
    for mat in mats:
        obj.data.materials.append(mat)
    for poly, key in zip(obj.data.polygons, keys):
        poly.material_index = key
    return k.smooth(obj, 80)


def pearl_wind():
    parts = fighter(PEARL_FIGHTER_Z)
    pearl_mats = [glow_mat(f"pearl{i}", index, emit, strength, 0.05, 0.1)
                  for i, (_, index, emit, strength) in enumerate(PEARL_BANDS)]
    tail_mats = {str(i): glow_mat(f"pearl_tail{i}", index, emit, strength, 0.25, 0.3)
                 for i, (_, index, emit, strength) in enumerate(TAIL_SHADES)}

    def shade(t, a):
        return str(sum(t >= start for start, _, _, _ in TAIL_SHADES[1:]))
    for i, (x, y, z, length, lean) in enumerate(PEARLS):
        parts.append(superellipsoid(f"pearl{i}", (x, y, z), pearl_mats))
        # Down the screen from the pearl, bending a little to one side at its end.
        zt = z - TAIL_DROP
        path = catmull([(x, y, zt), (x + 0.1 * lean, y - 0.35 * length, zt - 0.1),
                        (x + 0.55 * lean, y - 0.7 * length, zt - 0.25), (x + lean, y - length, zt - 0.4)], 8)
        widths = [profile_at(TAIL, j / (len(path) - 1)) for j in range(len(path))]
        parts.append(band(f"tail{i}", path, widths, [w * TAIL_SQUASH for w in widths], tail_mats, shade, segments=16))
    return parts


# --- 275: Soul of Zinglon ------------------------------------------------------------------------------------------

# The capsule (columns 6-18, rows 0-27): its half-width, half-length, how far its ends round off; the cradle (its
# lower half, CRADLE_D deep under its rim at RIM_Z) and the glass lid over it (LID_H high); the fighter's height in
# it. The cradle's inside glows, lightest down the capsule's middle and darker towards its outline, a shade a pixel
# as the sprite's: bands by how far out a point lies (0 on the middle line, 1 on the outline, seen from above:
# lower border, palette index, glowing in, glow). The lid's bands by its slope (the normal's z: lower border,
# palette index, alpha): a dark, denser rim (the sprite's outline), clear over the middle.
CAPSULE_W, CAPSULE_L, CAPSULE_END = 6.5, 14.0, 5.6
CRADLE_D, RIM_Z, LID_H, SOUL_FIGHTER_Z = 3.0, 3.25, 3.45, 1.45
CRADLE_BANDS = [(0.0, 0x3e, 0x3f, 0.5), (0.38, 0x3c, 0x3d, 0.4), (0.54, 0x3a, 0x3b, 0.3), (0.69, 0x35, 0x37, 0.2),
                (0.85, 0x33, 0x35, 0.12)]
LID_BANDS = [(-1.0, 0x35, 0.55), (0.45, 0x3e, 0.1)]


def capsule_section(t):
    """The capsule's half-width at the fraction t (-1 to 1) of its half-length."""
    end = abs(t) * CAPSULE_L - (CAPSULE_L - CAPSULE_END)
    if end <= 0:
        return CAPSULE_W
    return CAPSULE_W * math.sqrt(max(0.0, 1 - (end / CAPSULE_END) ** 2))


def capsule_out(co):
    """How far out a point lies in the capsule, seen from above: 0 on its middle line, 1 on its outline."""
    end = max(0.0, abs(co.y) - (CAPSULE_L - CAPSULE_END)) / CAPSULE_END
    return math.hypot((co.x - AXIS) / CAPSULE_W, end)


def capsule_shell(name, depth, sign, inner, mats, borders, segments=22, steps=36, field=None):
    """Half of the capsule's shell through its outline at z = RIM_Z: its lower half (sign -1, depth deep) or its
    upper one (sign 1, depth high), elliptical across; its faces facing out, or in (inner: the cradle's inside),
    painted in bands by the normal's z, or by field(point) (borders: the bands' lower borders but the first's;
    mats: one per band)."""
    bm = bmesh.new()
    rows = []
    for i in range(steps + 1):
        t = -1 + 2 * i / steps
        y = t * CAPSULE_L
        w = capsule_section(t)
        if w < 1e-3:
            rows.append([bm.verts.new((AXIS, y, RIM_Z))])
            continue
        d = depth * w / CAPSULE_W
        rows.append([bm.verts.new((AXIS + w * math.cos(math.pi * j / segments), y,
                                   RIM_Z + sign * d * math.sin(math.pi * j / segments))) for j in range(segments + 1)])
    for a, b in zip(rows, rows[1:]):
        for j in range(segments):
            if len(a) == 1:
                bm.faces.new((a[0], b[j + 1], b[j]))
            elif len(b) == 1:
                bm.faces.new((a[j], a[j + 1], b[0]))
            else:
                bm.faces.new((a[j], a[j + 1], b[j + 1], b[j]))
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    for f in bm.faces:
        f.normal_update()
        c = f.calc_center_median()
        out = Vector((c.x - AXIS, 0, c.z - RIM_Z)).normalized()
        if f.normal.dot(-out if inner else out) < 0:
            f.normal_flip()
    if field is None:
        keys = banded_by_normal(bm, borders)
    else:
        for t in borders:
            kit.split_along(bm, {v: field(v.co) for v in bm.verts}, t)
        bmesh.ops.triangulate(bm, faces=bm.faces[:])
        keys = [sum(field(f.calc_center_median()) > t for t in borders) for f in bm.faces]
    if sign > 0:
        # The lid is see-through: the game draws it blended, in the order of its triangles, without depth writes, so
        # its faces go from the bottom up (the camera looks down on it: its far parts first).
        bm.faces.ensure_lookup_table()
        order = sorted(range(len(bm.faces)), key=lambda i: (round(bm.faces[i].calc_center_median().z, 4), i))
        rank = {i: r for r, i in enumerate(order)}
        bm.faces.sort(key=lambda f: rank[f.index])
        bm.faces.index_update()
        keys = [keys[i] for i in order]
    obj = kit.from_bmesh(name, bm)
    for mat in mats:
        obj.data.materials.append(mat)
    for poly, key in zip(obj.data.polygons, keys):
        poly.material_index = key
    return k.smooth(obj, 80)


def soul_of_zinglon():
    parts = fighter(SOUL_FIGHTER_Z)
    cradle_mats = [glow_mat(f"cradle{i}", index, emit, strength, 0.1, 0.25)
                   for i, (_, index, emit, strength) in enumerate(CRADLE_BANDS)]
    parts.append(capsule_shell("cradle", CRADLE_D, -1, True, cradle_mats, [b[0] for b in CRADLE_BANDS[1:]],
                               field=capsule_out))
    # The cradle's outside, dark (the sprite's outline), a little under its inside.
    parts.append(capsule_shell("cradle_out", CRADLE_D + 0.25, -1, False,
                               [k.material("cradle_out", palette=0x33, metallic=0.3, roughness=0.3)], []))
    lid_mats = [k.material(f"lid{i}", palette=index, metallic=0.0, roughness=0.05, alpha=alpha,
                           emission=k.level_palette()[index], emission_strength=0.08)
                for i, (_, index, alpha) in enumerate(LID_BANDS)]
    parts.append(capsule_shell("lid", LID_H, 1, False, lid_mats, [b[0] for b in LID_BANDS[1:]]))
    return parts


# --- 277: Attractor ------------------------------------------------------------------------------------------------

# The four needles from the corners in at the fighter: their paths (from the outer end to the cap, (x, y)), and
# their caps' colours (palette index, glowing in): pink, pale blue, orange and lavender, as the sprite's tips.
NEEDLES = [
    ([(-11.6, 12.6), (-9.5, 10.5), (-7.5, 8.5), (-5.95, 6.95), (-5.0, 6.0)], (0x4c, 0x4d)),
    ([(10.8, 12.8), (9.2, 11.4), (7.6, 9.6), (6.55, 8.1), (6.05, 6.5), (5.45, 5.15), (5.05, 3.85)], (0x3e, 0x3f)),
    ([(10.6, -13.85), (9.1, -12.0), (8.1, -10.0), (7.55, -7.9), (7.2, -5.9), (7.0, -4.95)], (0x7c, 0x7d)),
    ([(-11.7, -12.8), (-9.0, -11.5), (-6.5, -10.4), (-5.3, -9.3), (-4.4, -8.15), (-4.0, -7.0)], (0x5c, 0x5d)),
]
# Their radius along them (from the outer end, as fractions of the length), how flat they are, the height they lie
# at, the caps' radius; their shades from the outer end in (from where, palette index, glowing in, glow: lighter
# towards the cap, as the sprite's).
NEEDLE_R = [(0.0, 0.22), (0.12, 0.7), (0.3, 1.02), (0.75, 1.18), (1.0, 1.2)]
NEEDLE_SQUASH, NEEDLE_Z, CAP_R = 0.85, 1.7, 1.05
NEEDLE_SHADES = [(0.0, 0x35, 0x37, 0.28), (0.35, 0x38, 0x39, 0.34), (0.7, 0x3b, 0x3c, 0.42)]


def attractor():
    parts = fighter()
    mats = {str(i): glow_mat(f"needle{i}", index, emit, strength, 0.45, 0.25)
            for i, (_, index, emit, strength) in enumerate(NEEDLE_SHADES)}

    def shade(t, a):
        return str(sum(t >= start for start, _, _, _ in NEEDLE_SHADES[1:]))
    for n, (points, (cap, cap_glow)) in enumerate(NEEDLES):
        path = catmull([(x, y, NEEDLE_Z) for x, y in points], 8)
        lengths = [0.0]
        for a, b in zip(path, path[1:]):
            lengths.append(lengths[-1] + (b - a).length)
        widths = [profile_at(NEEDLE_R, d / lengths[-1]) for d in lengths]
        parts.append(band(f"needle{n}", path, widths, [w * NEEDLE_SQUASH for w in widths], mats, shade, segments=14))
        cap_mat = glow_mat(f"needle_cap{n}", cap, cap_glow, 0.55, 0.1, 0.2)
        dome = k.ellipsoid(f"cap{n}", tuple(path[-1]), (CAP_R, CAP_R, CAP_R * NEEDLE_SQUASH * 1.05), cap_mat, 16, 10)
        parts.append(k.smooth(dome, 80))
    return parts


# --- 121: Ice Beam -------------------------------------------------------------------------------------------------

# The burst over the nose (rows 0-4, columns 9-15): a cut ice gem at GEM (x, y; its girdle's radius before it is
# stretched GEM_STRETCH times across, its girdle's height, its table's, its middle's height), shards of ice growing out
# of it (azimuth and tilt of each one's axis, degrees; its length, radius; where it starts, from the gem's middle);
# the two streams from under it down either side of the nose (the left one's path, mirrored; their half-width along
# them); the sparkles (x, y, size).
GEM = (AXIS, 11.85)
GEM_R, GEM_STRETCH, GEM_GIRDLE, GEM_TABLE, GEM_Z = 2.3, 1.5, 0.55, 1.95, 1.9
SHARDS = [(150.0, 38.0, 2.5, 0.62, (-0.7, 0.4)), (35.0, 40.0, 2.4, 0.6, (1.0, 0.45)),
          (95.0, 62.0, 2.2, 0.55, (0.15, 0.7)), (205.0, 30.0, 1.7, 0.5, (-1.6, -0.3))]
STREAM = [(-0.45, 9.8, 2.6), (-1.45, 8.5, 2.35), (-2.25, 7.25, 2.1), (-2.85, 5.95, 1.9), (-3.3, 4.6, 1.75),
          (-3.5, 3.3, 1.65), (-3.55, 2.05, 1.6)]
STREAM_W = [(0.0, 0.95), (0.5, 0.85), (0.75, 0.62), (0.92, 0.45), (1.0, 0.1)]
SPARKLES = [(5.5, 9.5, 0.95), (-4.5, 8.5, 0.85), (6.5, 4.5, 0.9), (-5.5, 3.5, 0.95)]
SPARKLE_Z = 2.2


def shard(name, length, radius, mat, sides=6):
    """An ice crystal: a hexagonal prism along +z with a pointed tip, its base at z = 0 (flat facets)."""
    bm = bmesh.new()
    ring = [(math.cos(2 * math.pi * i / sides + 0.3), math.sin(2 * math.pi * i / sides + 0.3)) for i in range(sides)]
    base = [bm.verts.new((radius * c, radius * s, 0.0)) for c, s in ring]
    top = [bm.verts.new((radius * 0.92 * c, radius * 0.92 * s, length * 0.62)) for c, s in ring]
    apex = bm.verts.new((0.0, 0.0, length))
    for i in range(sides):
        j = (i + 1) % sides
        bm.faces.new((base[i], base[j], top[j], top[i]))
        bm.faces.new((top[i], top[j], apex))
    bm.faces.new(list(reversed(base)))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return kit.flat_shade(kit.from_bmesh(name, bm, mat))


def ice_gem(name, mats):
    """A round cut gem (girdle, bezels, star facets, table) of radius GEM_R at the origin, stretched across."""
    pairs = []
    for i in range(8):
        a, b = 45.0 * i + 22.5, 45.0 * i
        pairs.append((kit.wall(a, GEM_R), "girdle"))
        r = math.radians(b)
        pairs.append((kit.facet(b, 0.9, (GEM_R * math.cos(r), GEM_R * math.sin(r), GEM_GIRDLE)), "bezel"))
        r = math.radians(a)
        pairs.append((kit.facet(a, 0.32, (1.05 * math.cos(r), 1.05 * math.sin(r), GEM_TABLE)), "star"))
    pairs += [(kit.flat(GEM_TABLE), "table"), (kit.flat(-0.4, below=True), "girdle")]
    obj = solid(name, pairs, mats)
    obj.data.transform(Matrix.Diagonal((GEM_STRETCH, 1.0, 1.0, 1.0)))
    return obj


def ice_beam():
    parts = fighter()
    light = glow_mat("ice_light", 0x3f, 0x3f, 0.5, 0.05, 0.06)
    ice = glow_mat("ice", 0x3d, 0x3e, 0.45, 0.05, 0.08)
    dark = glow_mat("ice_dark", 0x3b, 0x3c, 0.38, 0.05, 0.1)
    gem = ice_gem("ice_gem", {"table": light, "star": light, "bezel": ice, "girdle": dark})
    gx, gy = GEM
    gem.data.transform(Matrix.Translation((gx, gy, GEM_Z)))
    parts.append(gem)
    for i, (azimuth, tilt, length, radius, (ox, oy)) in enumerate(SHARDS):
        crystal = shard(f"shard{i}", length, radius, ice if i % 2 == 0 else light)
        a, t = math.radians(azimuth), math.radians(tilt)
        axis = Vector((math.cos(a) * math.cos(t), math.sin(a) * math.cos(t), math.sin(t)))
        turn = Vector((0, 0, 1)).rotation_difference(axis).to_matrix().to_4x4()
        crystal.data.transform(Matrix.Translation((gx + ox, gy + oy, GEM_Z + GEM_TABLE - 0.6)) @ turn)
        parts.append(crystal)
    mats = {"*": glow_mat("ice_stream", 0x39, 0x3b, 0.4, 0.2, 0.12),
            "core": glow_mat("ice_stream_core", 0x3c, 0x3d, 0.5, 0.1, 0.1)}
    for side in (1, -1):
        path = catmull([(AXIS + side * (x - AXIS), y, z) for x, y, z in STREAM], 6)
        widths = [profile_at(STREAM_W, j / (len(path) - 1)) for j in range(len(path))]
        parts.append(band(f"stream{side}", path, widths, [w * 0.75 for w in widths], mats,
                          lambda t, a: "core" if t < 0.4 and 30.0 < a < 150.0 else "*", segments=12))
    sparkle = glow_mat("ice_sparkle", 0x3e, 0x3f, 0.6, 0.0, 0.1)
    for i, (x, y, size) in enumerate(SPARKLES):
        for j, (length, width) in enumerate(((size, size * 0.38), (size * 0.38, size))):
            star = lozenge(f"sparkle{i}_{j}", length, width, size * 0.45, sparkle)
            star.data.transform(Matrix.Translation((x, y, SPARKLE_Z)))
            parts.append(star)
    return parts


# --- 123: Flare ----------------------------------------------------------------------------------------------------

# The ring of fire: its middle line (the sprite's red ring of pixels, pulled RING_IN towards the middle; the left half
# from the top round to the bottom, mirrored), its half-width, height and the height it lies at; its flames (how many
# waves round it, how high); the fighter's height and the deep red plate under it.
RING = [(0.5, 10.55), (-0.55, 9.55), (-1.6, 8.5), (-2.75, 7.3), (-3.55, 6.0), (-4.4, 4.75), (-5.5, 3.55),
        (-6.65, 2.4), (-7.75, 1.25), (-8.45, -0.1), (-8.45, -1.5), (-7.65, -2.65), (-6.75, -3.75), (-6.0, -5.0),
        (-5.15, -6.05), (-4.0, -7.1), (-2.6, -8.05), (-0.9, -8.6), (0.5, -8.7)]
RING_C, RING_W, RING_H, RING_Z, RING_IN = (AXIS, 0.6), 1.25, 0.95, 1.55, 0.3
FLAME_WAVES, FLAME_RISE = 9, 0.3
FLARE_FIGHTER_Z, FILL_Z, FILL_SCALE = 0.5, 0.45, 0.9


def flare():
    parts = fighter(FLARE_FIGHTER_Z)
    centre = Vector((*RING_C, 0))
    half = [Vector((x, y, 0)) for x, y in RING]
    half = [p - (p - centre).normalized() * RING_IN for p in half]
    loop = half + [Vector((2 * AXIS - p.x, p.y, 0)) for p in reversed(half[1:-1])]
    path = catmull([(p.x, p.y, RING_Z) for p in loop] + [(loop[0].x, loop[0].y, RING_Z)], 4)[:-1]
    n = len(path)
    heights = [RING_H + FLAME_RISE * math.sin(2 * math.pi * FLAME_WAVES * i / n) for i in range(n)]
    mats = {"hot": glow_mat("flare_hot", 0x7c, 0x7d, 0.58, 0.0, 0.85),
            "orange": glow_mat("flare_orange", 0x79, 0x7a, 0.52, 0.0, 0.85),
            "*": glow_mat("flare_red", 0x76, 0x77, 0.45, 0.0, 0.85),
            "dark": glow_mat("flare_dark", 0x73, 0x74, 0.32, 0.0, 0.85)}

    # The loop runs counter-clockwise, so its left (angle 0) is the side towards the fighter.
    def pick(t, a):
        if a < 55.0 or a > 320.0:
            return "hot"
        if a < 105.0:
            return "orange"
        return "*" if a < 210.0 else "dark"
    parts.append(band("ring", path, [RING_W] * n, heights, mats, pick, segments=16, closed=True))
    # The plate of deep red inside the ring, under the fighter.
    inner = [(centre.x + (p.x - centre.x) * FILL_SCALE, centre.y + (p.y - centre.y) * FILL_SCALE) for p in loop]
    if area(inner) < 0:
        inner.reverse()
    parts.append(relief("fill", inner, lambda x, y, d: FILL_Z + 0.25 * rounded(d, 0.8),
                        glow_mat("flare_fill", 0x74, 0x75, 0.3, 0.0, 0.7)))
    return parts


# --- 3: MegaLaser Dual ---------------------------------------------------------------------------------------------

# The orb (columns 2-22, rows 3-23): its middle, radius, height over its middle and its middle's height (its underside
# cut off at z = 0); its shell's bands by the normal's z (lower border, palette index, glowing in, glow); the slots
# (x from, to; y from, to; how deep) and the bars in them (half-width, height).
ORB_C, ORB_R, ORB_H, ORB_Z = (0.5, 0.5), 10.42, 8.6, 3.0
ORB_BANDS = [(-1.0, 0xe3, None, 0.0), (0.16, 0xe6, 0xe6, 0.12), (0.4, 0xe8, 0xe7, 0.14), (0.62, 0xe9, 0xe8, 0.15),
             (0.82, 0xea, 0xe9, 0.16)]
SLOTS = [(-4.95, -0.05), (1.05, 5.95)]
SLOT_Y, SLOT_DEPTH = (-7.0, 8.0), 1.55
BAR_W, BAR_H = 1.45, 0.95


def orb_height(x, y):
    dx, dy = (x - ORB_C[0]) / ORB_R, (y - ORB_C[1]) / ORB_R
    return ORB_Z + ORB_H * math.sqrt(max(0.0, 1.0 - dx * dx - dy * dy))


def ellipsoid_mesh(name, radii, mat, floor=None):
    """A UV sphere scaled to radii round the orb's middle (its underside cut flat at z = floor)."""
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=48, v_segments=24, radius=1.0)
    rx, ry, rz = radii
    for v in bm.verts:
        z = v.co.z * rz if floor is None else max(v.co.z * rz, floor - ORB_Z)
        v.co = Vector((ORB_C[0] + v.co.x * rx, ORB_C[1] + v.co.y * ry, ORB_Z + z))
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=1e-4)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return kit.from_bmesh(name, bm, mat)


def canonical(obj):
    """Rebuilds the object's mesh in a fixed order (its vertices by position, each face starting at its smallest
    corner, the faces by their corners): the exact boolean returns its result in an order that changes from run to
    run, and the rest of the script and the export follow that order."""
    me = obj.data

    def key(co):
        return (round(co.x, 5), round(co.y, 5), round(co.z, 5))
    faces = []
    for poly in me.polygons:
        corners = [key(me.vertices[i].co) for i in poly.vertices]
        start = corners.index(min(corners))
        faces.append((corners[start:] + corners[:start], poly.material_index))
    faces.sort()
    verts = sorted({c for corners, _ in faces for c in corners})
    index = {c: i for i, c in enumerate(verts)}
    mesh = bpy.data.meshes.new(me.name)
    mesh.from_pydata(verts, [], [[index[c] for c in corners] for corners, _ in faces])
    for mat in me.materials:
        mesh.materials.append(mat)
    for poly, (_, material) in zip(mesh.polygons, faces):
        poly.material_index = material
    obj.data = mesh
    bpy.data.meshes.remove(me)
    return obj


def megalaser_dual():
    shell_mats = [k.material(f"orb{i}", palette=index, metallic=0.2, roughness=0.35) if emit is None else
                  glow_mat(f"orb{i}", index, emit, strength, 0.2, 0.32)
                  for i, (_, index, emit, strength) in enumerate(ORB_BANDS)]
    slot_mat = k.material("orb_slot", palette=0xe3, metallic=0.3, roughness=0.5)
    orb = ellipsoid_mesh("orb", (ORB_R, ORB_R, ORB_H), shell_mats[0], floor=0.0)
    for mat in shell_mats[1:] + [slot_mat]:
        orb.data.materials.append(mat)
    # The slots: rounded troughs cut into the shell, SLOT_DEPTH deep (a stadium prism minus a sphere SLOT_DEPTH
    # smaller, so that their floors follow the ball).
    y0, y1 = SLOT_Y
    for i, (x0, x1) in enumerate(SLOTS):
        r, xc = (x1 - x0) / 2, (x0 + x1) / 2
        outline = ([(xc + r * math.cos(math.pi + math.pi * j / 10), y0 + r + r * math.sin(math.pi + math.pi * j / 10))
                    for j in range(11)] +
                   [(xc + r * math.cos(math.pi * j / 10), y1 - r + r * math.sin(math.pi * j / 10)) for j in range(11)])
        cutter = kit.prism(f"slot{i}", outline, ORB_Z, ORB_Z + ORB_H + 3.0, slot_mat)
        core = ellipsoid_mesh(f"slot_core{i}", (ORB_R - SLOT_DEPTH, ORB_R - SLOT_DEPTH, ORB_H - SLOT_DEPTH), slot_mat)
        canonical(kit.boolean(cutter, core, "DIFFERENCE"))
        canonical(kit.boolean(orb, cutter, "DIFFERENCE"))
    # The shell's faces in their bands; the slots' faces stay dark.
    slot_index = kit.slot_of(orb, slot_mat)
    bm = bmesh.new()
    bm.from_mesh(orb.data)
    bands = banded_by_normal(bm, [b[0] for b in ORB_BANDS[1:]])
    for f, band_index in zip(bm.faces, bands):
        if f.material_index != slot_index:
            f.material_index = band_index
    bm.to_mesh(orb.data)
    bm.free()
    parts = [k.smooth(orb, 50)]
    # The bars: glowing blue, lying in the slots along the ball's curve, a pale line along each.
    bar_mats = {"*": glow_mat("bar", 0x9a, 0x9b, 0.55, 0.1, 0.2),
                "core": glow_mat("bar_core", 0x9e, 0x8c, 0.6, 0.0, 0.15)}
    count = 26
    for i, (x0, x1) in enumerate(SLOTS):
        xc = (x0 + x1) / 2
        path = []
        for j in range(count):
            y = y0 + 0.35 + (y1 - y0 - 0.7) * j / (count - 1)
            path.append((xc, y, orb_height(xc, y) - SLOT_DEPTH * 0.55))
        widths = [BAR_W * v for v in taper(count, (0.0, 0.0), 0.25)]
        parts.append(band(f"bar{i}", path, widths, [w * BAR_H / BAR_W for w in widths], bar_mats,
                          lambda t, a: "core" if 74.0 < a < 112.0 and 0.12 < t < 0.88 else "*", segments=16))
    return parts


# --- Building ------------------------------------------------------------------------------------------------------

MODELS = [
    ("pu_repulsor", 271, repulsor),
    ("pu_pearl_wind", 273, pearl_wind),
    ("pu_soul_of_zinglon", 275, soul_of_zinglon),
    ("pu_attractor", 277, attractor),
    ("pu_ice_beam", 121, ice_beam),
    ("pu_flare", 123, flare),
    ("pu_megalaser_dual", 3, megalaser_dual),
]


def triangulate(objects):
    """Splits every face into triangles here, the same way every run (the exporter's own split of the n-gons changed
    after a --check render), keeping the custom normals (polish_k_pod.triangulate)."""
    for obj in objects:
        mod = obj.modifiers.new("triangulate", "TRIANGULATE")
        mod.quad_method = "BEAUTY"
        mod.ngon_method = "BEAUTY"
        mod.min_vertices = 4
        mod.keep_custom_normals = True
        kit.apply(obj)
    return objects


def check(opts, label, objects, sprite, keep=None):
    """The silhouette against the sprite in powerups.png; keep: which palette indices of the sprite count (all by
    default)."""
    if "check" not in opts:
        return None
    sys.path.insert(0, os.path.join(HERE, "..", ".."))
    from sprite_profile import sprite_indices
    sheet = opts["check"]
    sheet = os.path.join(sheet, "powerups.png") if os.path.isdir(sheet) else sheet
    mask = [[p is not None and (keep is None or keep(p)) for p in row] for row in sprite_indices(sheet, sprite, True)]
    return kit.compare(label, kit.coverage(objects, 24, 28), mask)


def build():
    opts = kit.options()
    for name, sprite, make in MODELS:
        if not kit.wanted(opts, name):
            continue
        k.reset()
        FIGHTER.clear()
        parts = make()
        for obj in parts:
            kit.apply(obj)
            kit.drop_unused_materials(obj)
        triangulate(parts)
        bpy.context.view_layer.update()
        check(opts, "%s (powerups %d)" % (name, sprite), parts, sprite)
        if sprite == 121 and FIGHTER:
            check(opts, "the fighter alone (its own pixels in powerups 121)", FIGHTER, 121, is_fighter)
        bpy.context.scene.view_settings.view_transform = "Standard"
        kit.report(name, parts, os.path.join(kit.outdir(opts), name + ".glb"))
        if "preview" in opts:
            kit.preview(opts["preview"] + name, parts, (24, 28), scale=16, distance=0.6)


if __name__ == "__main__":
    build()
