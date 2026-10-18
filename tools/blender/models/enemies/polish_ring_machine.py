"""The ring machine of the lava levels and episode 6 (sheet 3 sprite 195, 2x2: a 21 x 24 machine in
the 24 x 28 cell; static; sky and top layers; 157 of them: LAVA EXIT, LAVA RUN, SIDE EXIT, ROOST,
COLLECTOR, INVADERS), polished (2026-10-18; it replaces later_episodes.py's ring_machine(), a plain
grey torus with three red balls). models.cfg: sprite 3 195 ring_machine yaw=0.

As the 4x upscale draws it: a dark steel frame round a hole (columns 2-22 of rows 7-24; the hole,
see-through, columns 6-18 of rows 12-19), a red dome on top (columns 7-17 of rows 1-7: a glossy
cap, its glare at the upper left) over a dark grey hub that hangs from it into the hole's top
(columns 9-15 of rows 7-15, lit along its top edge). Steel plates lie on the frame: two shoulders
slanting out and down from the dome (rows 7-13), two jaws curving round the hole's lower half
(rows 16-24), a light crest along their inner edges, each jaw ending in two prongs at the bottom,
a foot (columns 4-7) and a tusk (columns 9-11) with a notch between them. Small red lights glow
where shoulder and jaw meet (columns 3-4 and 20-21 of rows 13-15) and between the tusks at the
bottom (columns 11-13 of rows 20-23). Everything else is the frame's near-black steel, which the
sprite draws as its outline and as the grooves between the parts.

The parts are solids over outlines traced from the upscale (relief(): a triangulated top with
rounded edges, straight walls and a flat underside, its colours cut in along smooth borders); the
dome is a polar mesh (dome()), its glare painted on in three shades. Colours follow the sprite's
indices (ramp 0 greys, ramp 4 reds); the dome and the hub glow a little in their own colours,
since the game's camera sees mostly their sides away from the sun, and the lights glow.
polish_arrow_purple.py and polish_brain_clamp.py use relief() and dome() too.

The sprite is symmetric about its column 12.5 (x 0.5 here): the machine is built about x = 0 from
the left half's outlines and their mirror images, and moved there (AXIS_X). Points are given as
(column, row) of the sprite (px()). Origin at the sprite's centre (pixel 12, 14); +Y up the sprite,
+Z towards the camera.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <dir with enemy_3.png,
or the sheet itself> (the silhouette), --preview <prefix>.
"""
import math
import os
import sys

import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Vector, geometry

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
from polish_sphere_nozzle import smoothstep, split_along  # noqa: E402

AXIS_X = 0.5


def px(c, r):
    """A point of the sprite, (column, row) from its top left corner, in the model's coordinates
    about the axis (x = 0 is the sprite's column 12.5)."""
    return (c - 12.5, 14.0 - r)


# The frame's outline, its left half from the top middle down to the bottom middle (column, row):
# the dome's dark rim, the shoulders flaring out to the full width (rows 7-10), the straight sides,
# the rounded lower corners, the left foot, the notch (columns 8-9 from row 23) and the middle tab.
OUTLINE_LEFT = [(12.5, 0.85), (11.0, 0.95), (9.6, 1.12), (8.9, 1.5), (8.4, 2.0), (7.85, 2.6), (7.45, 3.2),
                (7.05, 3.9), (6.7, 4.6), (6.4, 5.3), (6.1, 6.0), (5.8, 6.55), (5.2, 6.9), (4.4, 7.2), (3.7, 7.65),
                (3.2, 8.1), (2.75, 8.6), (2.35, 9.15), (2.05, 9.7), (2.0, 10.5), (2.0, 19.2), (2.2, 19.8),
                (2.3, 20.6), (2.55, 21.2), (2.85, 21.9), (3.25, 22.5), (3.7, 23.1), (4.2, 23.85), (4.75, 24.4),
                (5.4, 24.85), (6.3, 25.0), (7.4, 25.0), (7.95, 24.7), (8.0, 23.25), (8.2, 22.98), (8.5, 22.92),
                (8.8, 22.98), (9.0, 23.25), (9.05, 24.8), (9.4, 25.0), (11.0, 25.0)]
# The hole (see-through): its middle, half-width, and its upper half an ellipse HOLE_TOP high, its
# lower half a superellipse of power HOLE_POWER, HOLE_BOTTOM deep (narrowing to a blunt point).
HOLE_CENTRE = (12.5, 15.0)
HOLE_HALF_WIDTH, HOLE_TOP, HOLE_BOTTOM, HOLE_POWER = 6.5, 4.2, 4.35, 1.6
# The plates on the frame (left ones; the right ones are their mirror images).
SHOULDER_LEFT = [(9.3, 7.2), (9.55, 8.0), (9.5, 9.1), (9.05, 10.0), (8.25, 10.95), (7.3, 11.9), (6.4, 12.65),
                 (5.4, 13.0), (4.2, 13.0), (3.3, 12.6), (2.85, 11.6), (2.8, 10.4), (3.15, 9.3), (3.85, 8.3),
                 (4.9, 7.45), (6.2, 6.9), (7.9, 6.8)]
JAW_LEFT = [(3.0, 16.5), (4.1, 16.25), (5.3, 16.3), (6.05, 16.6), (6.6, 17.05), (7.5, 17.95), (8.35, 18.6),
            (9.1, 19.1), (9.9, 19.55), (10.7, 19.85), (11.1, 20.25), (11.1, 23.15), (10.8, 23.7), (10.0, 23.75),
            (9.6, 23.3), (9.5, 22.2), (9.2, 21.65), (8.4, 21.45), (7.6, 21.55), (7.15, 22.0), (7.05, 22.6),
            (7.0, 23.3), (6.6, 23.8), (5.6, 23.85), (4.85, 23.45), (4.1, 22.4), (3.45, 21.1), (3.05, 19.7),
            (2.9, 18.1)]
# The hub under the dome: straight sides a little wider below, its bottom rounded (row 15).
HUB = [(10.4, 7.0), (12.5, 6.9), (14.6, 7.0), (15.05, 7.8), (15.3, 9.3), (15.7, 11.0), (16.0, 12.5),
       (15.75, 13.7), (15.0, 14.6), (13.8, 15.1), (12.5, 15.2), (11.2, 15.1), (10.0, 14.6), (9.25, 13.7),
       (9.0, 12.5), (9.3, 11.0), (9.7, 9.3), (9.95, 7.8)]
# The dome: its middle, the red cap's half-axes in plan, its base's height and its height above it
# (it stands on the frame, whose rounded edge round it is the sprite's dark rim); the glare's middle
# and size in plan, and the borders of its shades (in units of that size).
DOME_CENTRE = (12.5, 4.6)
DOME_RADII, DOME_BASE, DOME_HEIGHT = (5.15, 3.0), 0.9, 4.4
DOME_LOWER_POWER = 3.2  # its lower half squarer in plan: the sprite draws its foot nearly straight
GLARE, GLARE_SIZE, GLARE_BANDS = (11.2, 4.3), (2.5, 1.7), (0.22, 0.55, 1.0)
# The lights: the left side light (middle, half-axes in plan), the bottom light (a rounded block:
# columns 11-14 of rows 20.4-23.6).
SIDE_LIGHT, SIDE_LIGHT_RADII = (4.0, 14.45), (1.05, 1.55)
BOTTOM_LIGHT = [(11.05, 20.4), (13.95, 20.4), (13.95, 23.6), (11.05, 23.6)]

# Heights: the frame's top and underside, its rounded outer edge; the plates' top, crown and rounded
# edge; the jaws' crest (along the hole, CREST from its edge) and its light band; the hub's top.
FRAME_TOP, FRAME_BOTTOM, FRAME_RIM = 0.6, -2.4, 1.1
PLATE_TOP, PLATE_CROWN, PLATE_RIM = 2.3, 0.35, 0.85
CREST, CREST_WIDTH, CREST_RISE = 1.6, 1.1, 0.45
CREST_PAINT = (0.9, 2.5)  # the light band on the jaws: this far from the hole's edge
TUSKS = (3.5, -6.0)       # the tusks, painted light too: |x| below this, y below this
HUB_TOP, HUB_RIM, HUB_LIGHT = 3.6, 2.4, 8.9  # HUB_LIGHT: the light band's lower edge (row)


# --- Outlines -------------------------------------------------------------------------------------

def to_model(points):
    return [px(c, r) for c, r in points]


def mirrored(points):
    """The mirror image of a polygon across x = 0, in the same turning direction."""
    return [(-x, y) for x, y in reversed(points)]


def ccw(points):
    area = sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(points, points[1:] + points[:1]))
    return points if area > 0 else list(reversed(points))


def chaikin(points, iterations=2):
    pts = list(points)
    for _ in range(iterations):
        out = []
        for i in range(len(pts)):
            (x0, y0), (x1, y1) = pts[i], pts[(i + 1) % len(pts)]
            out += [(0.75 * x0 + 0.25 * x1, 0.75 * y0 + 0.25 * y1), (0.25 * x0 + 0.75 * x1, 0.25 * y0 + 0.75 * y1)]
        pts = out
    return pts


def resample(points, spacing):
    """A closed polygon resampled to points about `spacing` apart along its outline."""
    n = len(points)
    lengths = [math.dist(points[i], points[(i + 1) % n]) for i in range(n)]
    total = sum(lengths)
    count = max(8, int(round(total / spacing)))
    out, i, walked = [], 0, 0.0
    for c in range(count):
        target = total * c / count
        while walked + lengths[i] < target:
            walked += lengths[i]
            i += 1
        t = (target - walked) / lengths[i] if lengths[i] > 0 else 0.0
        (x0, y0), (x1, y1) = points[i], points[(i + 1) % n]
        out.append((x0 + (x1 - x0) * t, y0 + (y1 - y0) * t))
    return out


def outline():
    left = to_model(OUTLINE_LEFT)
    right = [(-x, y) for x, y in reversed(left[1:-1])]
    return ccw(chaikin(left + [(0.0, left[-1][1])] + right, 1))


def hole():
    cx, cy = px(*HOLE_CENTRE)
    points = []
    for i in range(96):
        a = 2 * math.pi * i / 96
        c, s = math.cos(a), math.sin(a)
        if s >= 0:
            points.append((cx + HOLE_HALF_WIDTH * c, cy + HOLE_TOP * s))
        else:
            p = HOLE_POWER
            points.append((cx + HOLE_HALF_WIDTH * math.copysign(abs(c) ** (2 / p), c),
                           cy - HOLE_BOTTOM * abs(s) ** (2 / p)))
    return ccw(points)


# --- Distances and insides ------------------------------------------------------------------------

class Region:
    """Polygons filled even-odd (holes stay open): inside tests and distances to their outlines."""

    def __init__(self, polys):
        self.polys = polys
        a, b = [], []
        for poly in polys:
            for i in range(len(poly)):
                a.append(poly[i])
                b.append(poly[(i + 1) % len(poly)])
        self.a, self.b = np.array(a, dtype=float), np.array(b, dtype=float)

    def inside(self, pts):
        pts = np.asarray(pts, dtype=float)
        px_, py_ = pts[:, :1], pts[:, 1:2]
        ax, ay, bx, by = self.a[:, 0][None], self.a[:, 1][None], self.b[:, 0][None], self.b[:, 1][None]
        straddle = (ay > py_) != (by > py_)
        with np.errstate(divide="ignore", invalid="ignore"):
            cross_x = ax + (py_ - ay) * (bx - ax) / np.where(by - ay == 0, 1e-12, by - ay)
        return (straddle & (px_ < cross_x)).sum(1) % 2 == 1

    def distance(self, pts):
        pts = np.asarray(pts, dtype=float)
        d = self.b - self.a
        length2 = np.maximum((d * d).sum(1), 1e-12)
        rel = pts[:, None, :] - self.a[None]
        t = np.clip((rel * d[None]).sum(2) / length2[None], 0.0, 1.0)
        nearest = self.a[None] + t[:, :, None] * d[None]
        return np.sqrt(((pts[:, None, :] - nearest) ** 2).sum(2)).min(1)


def round_edge(d, r):
    """0 at the outline rising as a quarter circle to 1 at distance r inside."""
    t = min(1.0, max(0.0, d / r))
    return math.sqrt(max(0.0, 1.0 - (1.0 - t) ** 2))


# --- Solids ---------------------------------------------------------------------------------------

def relief(name, polys, height, mats, paint=None, side="side", bottom=-1.0, spacing=0.32, borders=(),
           smooth_angle=50.0, band=None):
    """A solid filling the polygons (even-odd: holes stay open): its top at height(x, y, d), d the
    distance to the outline, straight walls down to `bottom` along the outline, a flat underside.
    paint(x, y, d) names a top face's material (mats: name -> material; `side` names the walls'
    and underside's); borders [(field(x, y, d), threshold), ...] are cut into the top first, so
    that colours change along smooth lines. band: grid points farther than this from the outline
    are kept only on a lattice twice as coarse (flat middles need fewer triangles)."""
    region = Region(polys)
    boundary, edges = [], []
    for poly in polys:
        ring = resample(poly, spacing)
        start = len(boundary)
        boundary += ring
        edges += [(start + i, start + (i + 1) % len(ring)) for i in range(len(ring))]
    xs = [p[0] for p in boundary]
    ys = [p[1] for p in boundary]
    grid, coarse = [], []
    row_step = spacing * math.sqrt(3) / 2
    for j in range(int((max(ys) - min(ys)) / row_step) + 2):
        y = min(ys) + j * row_step
        shift = spacing / 2 if j % 2 else 0.0
        for i in range(int((max(xs) - min(xs)) / spacing) + 2):
            grid.append((min(xs) + shift + i * spacing, y))
            coarse.append(j % 2 == 0 and i % 2 == 0)
    grid, coarse = np.array(grid), np.array(coarse)
    keep = region.inside(grid)
    grid, coarse = grid[keep], coarse[keep]
    d = region.distance(grid)
    keep = d > 0.45 * spacing
    if band is not None:
        keep &= (d <= band) | coarse
    grid = grid[keep]
    points = [Vector(p) for p in boundary] + [Vector(tuple(p)) for p in grid]
    verts, _e, faces, *_ = geometry.delaunay_2d_cdt(points, edges, [], 0, 1e-6)
    tris = [f for f in faces if len(f) == 3]
    centroids = np.array([[sum(verts[i].x for i in f) / 3, sum(verts[i].y for i in f) / 3] for f in tris])
    tris = [f for f, keep in zip(tris, region.inside(centroids)) if keep]

    bm = bmesh.new()
    top = [bm.verts.new((v.x, v.y, 0.0)) for v in verts]
    for f in tris:
        try:
            bm.faces.new([top[i] for i in f])
        except ValueError:
            pass
    for v in [v for v in bm.verts if not v.link_faces]:
        bm.verts.remove(v)
    distance = {}

    def dist(v):
        if v not in distance:
            distance[v] = float(region.distance([(v.co.x, v.co.y)])[0])
        return distance[v]

    on_outline = set(v for v in bm.verts if dist(v) < 1e-4)
    for field, threshold in borders:
        values = {v: field(v.co.x, v.co.y, dist(v)) for v in bm.verts}
        made = split_along(bm, values, threshold)
        for v in made:  # new vertices on the outline stay on it
            if any(len(e.link_faces) == 1 for e in v.link_edges):
                on_outline.add(v)
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    top_faces = list(bm.faces)
    keys = []
    for f in top_faces:
        c = f.calc_center_median()
        d = sum(0.0 if v in on_outline else dist(v) for v in f.verts) / len(f.verts)
        keys.append(paint(c.x, c.y, d) if paint else "top")
    for v in bm.verts:
        v.co.z = height(v.co.x, v.co.y, 0.0 if v in on_outline else dist(v))

    # The walls along the outline and the flat underside.
    rim_edges = [e for e in bm.edges if len(e.link_faces) == 1]
    lower = {}
    for e in rim_edges:
        for v in e.verts:
            if v not in lower:
                lower[v] = bm.verts.new((v.co.x, v.co.y, bottom))
    for e in rim_edges:
        a, b = e.verts
        bm.faces.new([b, a, lower[a], lower[b]])
    loop_points = list(lower.keys())
    index = {v: i for i, v in enumerate(loop_points)}
    under, _e2, under_faces, under_orig, *_ = geometry.delaunay_2d_cdt(
        [Vector((v.co.x, v.co.y)) for v in loop_points], [(index[e.verts[0]], index[e.verts[1]]) for e in rim_edges],
        [], 0, 1e-6)
    out_to_lower = {}
    for i, o in enumerate(under_orig):
        if o:
            out_to_lower[i] = lower[loop_points[o[0]]]
    under_tris = [f for f in under_faces if len(f) == 3 and all(i in out_to_lower for i in f)]
    centres = np.array([[sum(under[i].x for i in f) / 3, sum(under[i].y for i in f) / 3] for f in under_tris])
    for f, keep in zip(under_tris, region.inside(centres) if len(under_tris) else []):
        if keep:
            try:
                bm.faces.new([out_to_lower[i] for i in reversed(f)])
            except ValueError:
                pass
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    face_keys = {f: key for f, key in zip(top_faces, keys)}
    mesh = bpy.data.meshes.new(name)
    order = [f for f in bm.faces]
    names = []
    for f in order:
        key = face_keys.get(f, side)
        if key not in names:
            names.append(key)
    for key in names:
        mesh.materials.append(mats[key])
    for f in order:
        f.material_index = names.index(face_keys.get(f, side))
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    return k.smooth(obj, smooth_angle)


def dome(name, centre, radii, base, height, mats, paint, borders=(), rings=12, segments=44, skirt=0.8,
         lower_power=2.0):
    """A dome over an ellipse (centre and half-axes in plan, model coordinates): rings of the
    ellipse rising as a quarter ellipse from `base` to `base + height`, a short skirt below (the
    plan's lower half a superellipse of power lower_power). paint(x, y, z) names a face's
    material; borders [(field(x, y, z), threshold), ...] are cut in first, so that the colours
    change along smooth lines."""
    cx, cy = centre
    rows = [(1.0, base - skirt)]
    for i in range(rings):
        a = (math.pi / 2) * i / rings
        rows.append((math.cos(a), base + height * math.sin(a)))

    def plan(j):
        a = 2 * math.pi * j / segments
        c, sn = math.cos(a), math.sin(a)
        if sn >= 0:
            return c, sn
        p = lower_power
        return math.copysign(abs(c) ** (2 / p), c), -abs(sn) ** (2 / p)

    verts = [[Vector((cx + radii[0] * s * plan(j)[0], cy + radii[1] * s * plan(j)[1], z)) for j in range(segments)]
             for s, z in rows]
    obj = k.loft(name, verts, None, start_point=(cx, cy, base - skirt), end_point=(cx, cy, base + height))
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    for field, threshold in borders:
        split_along(bm, {v: field(v.co.x, v.co.y, v.co.z) for v in bm.verts}, threshold)
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    keys = []
    for f in bm.faces:
        c = f.calc_center_median()
        keys.append(paint(c.x, c.y, c.z))
    bm.to_mesh(obj.data)
    bm.free()
    names = []
    for poly, key in zip(obj.data.polygons, keys):
        if key not in names:
            names.append(key)
            obj.data.materials.append(mats[key])
        poly.material_index = names.index(key)
    k.recalc_normals(obj)
    return k.smooth(obj, 60)


# --- The parts ------------------------------------------------------------------------------------

def frame(mats):
    """The frame: the whole outline round the hole, its outer edge rounded."""
    return relief("frame", [outline(), hole()],
                  lambda x, y, d: FRAME_TOP - 1.2 + 1.2 * round_edge(d, FRAME_RIM), mats,
                  paint=lambda x, y, d: "frame", side="frame", bottom=FRAME_BOTTOM, spacing=0.6, band=1.5)


def plate(name, points, mats, crest=False):
    """A steel plate lying on the frame: rounded edges, a gentle crown; the jaws a crest along the
    hole, painted light."""
    poly = ccw(chaikin(points, 1))
    ring = Region([hole()])

    def to_hole(x, y):
        return float(ring.distance([(x, y)])[0])

    def height(x, y, d):
        z = PLATE_TOP - 1.4 + 1.4 * round_edge(d, PLATE_RIM) + PLATE_CROWN * smoothstep(0.5, 2.5, d)
        if crest:
            z += CREST_RISE * math.exp(-((to_hole(x, y) - CREST) / CREST_WIDTH) ** 2) * smoothstep(0.2, 0.9, d)
        return z

    def paint(x, y, d):
        if d < 0.35:
            return "plate_side"
        if crest and CREST_PAINT[0] < to_hole(x, y) < CREST_PAINT[1]:
            return "plate_light"
        if crest and abs(x) < TUSKS[0] and y < TUSKS[1]:
            return "plate_light"
        return "plate"

    borders = [(lambda x, y, d: d, 0.35)]
    if crest:
        borders += [(lambda x, y, d: to_hole(x, y), CREST_PAINT[0]), (lambda x, y, d: to_hole(x, y), CREST_PAINT[1])]
    return relief(name, [poly], height, mats, paint=paint, side="plate_side", bottom=0.0, borders=borders,
                  spacing=0.36, band=3.0 if crest else 1.3)


def hub(mats):
    """The dark hub under the dome, its top edge catching the light."""
    poly = ccw(chaikin(to_model(HUB), 2))

    def height(x, y, d):
        return 0.6 + (HUB_TOP - 0.6) * round_edge(d, HUB_RIM)

    def paint(x, y, d):
        return "hub_light" if y > px(0, HUB_LIGHT)[1] else "hub"

    return relief("hub", [poly], height, mats, paint=paint, side="hub", bottom=0.0, spacing=0.38,
                  borders=[(lambda x, y, d: y, px(0, HUB_LIGHT)[1])])


def red_dome(mats):
    """The red dome on the frame (whose rounded edge round it is the sprite's dark rim), its glare
    at the upper left, its foot dark."""
    gx, gy = px(*GLARE)

    def glare(x, y, z):
        return ((x - gx) / GLARE_SIZE[0]) ** 2 + ((y - gy) / GLARE_SIZE[1]) ** 2

    def paint(x, y, z):
        if z < DOME_BASE + 0.3:
            return "dome_rim"
        q = glare(x, y, z)
        return ("dome_glare_core", "dome_glare", "dome_glare_outer", "dome")[sum(q >= t for t in GLARE_BANDS)]

    borders = [(lambda x, y, z: z, DOME_BASE + 0.3)] + [(glare, t) for t in GLARE_BANDS]
    return dome("dome", px(*DOME_CENTRE), DOME_RADII, DOME_BASE, DOME_HEIGHT, mats, paint, borders,
                lower_power=DOME_LOWER_POWER)


def lights(mats):
    """The red lights: a capsule either side, between shoulder and jaw, hottest on top; a rounded
    block between the tusks."""
    lx, ly = px(*SIDE_LIGHT)
    for name, x in (("light_l", lx), ("light_r", -lx)):
        obj = k.ellipsoid(name, (x, ly, 0.75), (SIDE_LIGHT_RADII[0], SIDE_LIGHT_RADII[1], 1.35), None, 20, 10)
        obj.data.materials.append(mats["light"])
        obj.data.materials.append(mats["light_hot"])
        for poly in obj.data.polygons:
            c = poly.center
            poly.material_index = 1 if c.z > 1.55 and c.y > ly - 0.5 else 0
        k.smooth(obj, 60)
    block = ccw(chaikin(to_model(BOTTOM_LIGHT), 2))
    cx, cy = px(12.5, 21.5)

    def hot(x, y, d):
        return ((x - cx) / 1.0) ** 2 + ((y - cy) / 1.1) ** 2

    relief("bottom_light", [block], lambda x, y, d: 1.0 + 1.5 * round_edge(d, 0.9), mats,
           paint=lambda x, y, d: "light_hot" if hot(x, y, d) < 1.0 else "light", side="light", bottom=0.0,
           spacing=0.3, borders=[(hot, 1.0)])


def materials():
    pal = k.level_palette()
    return {
        "frame": k.material("ringm_frame", palette=0x02, metallic=0.5, roughness=0.42),
        "plate": k.material("ringm_plate", palette=0x0a, metallic=0.4, roughness=0.32),
        "plate_light": k.material("ringm_plate_light", palette=0x0c, metallic=0.4, roughness=0.28),
        "plate_side": k.material("ringm_plate_side", palette=0x06, metallic=0.45, roughness=0.35),
        # The hub is a dark rounded bell whose side the game's camera sees is turned from the sun: a
        # little light of its own keeps it grey.
        "hub": k.material("ringm_hub", palette=0x07, metallic=0.3, roughness=0.32, emission=pal[0x05],
                          emission_strength=0.35),
        "hub_light": k.material("ringm_hub_light", palette=0x0b, metallic=0.45, roughness=0.25),
        "dome": k.material("ringm_dome", palette=0x47, metallic=0.2, roughness=0.25, emission=pal[0x46],
                           emission_strength=0.35),
        "dome_glare_outer": k.material("ringm_dome_glare_outer", palette=0x48, metallic=0.2, roughness=0.22,
                                       emission=pal[0x47], emission_strength=0.35),
        "dome_glare": k.material("ringm_dome_glare", palette=0x4a, metallic=0.2, roughness=0.2,
                                 emission=pal[0x48], emission_strength=0.35),
        "dome_glare_core": k.material("ringm_dome_glare_core", palette=0x4d, metallic=0.15, roughness=0.15,
                                      emission=pal[0x4b], emission_strength=0.4),
        "dome_rim": k.material("ringm_dome_rim", palette=0x43, metallic=0.3, roughness=0.35),
        "light": k.material("ringm_light", palette=0x47, roughness=0.3, emission=pal[0x48], emission_strength=1.0),
        "light_hot": k.material("ringm_light_hot", palette=0x4b, roughness=0.25, emission=pal[0x4b],
                                emission_strength=1.1),
    }


def build_machine(mats):
    frame(mats)
    for points, name, crest in ((SHOULDER_LEFT, "shoulder", False), (JAW_LEFT, "jaw", True)):
        left = to_model(points)
        plate(name + "_l", left, mats, crest)
        plate(name + "_r", mirrored(left), mats, crest)
    hub(mats)
    red_dome(mats)
    lights(mats)
    for obj in bpy.context.scene.objects:
        if obj.type == "MESH":
            obj.data.transform(Matrix.Translation((AXIS_X, 0.0, 0.0)))


def triangles():
    depsgraph = bpy.context.evaluated_depsgraph_get()
    total = 0
    for obj in bpy.context.scene.objects:
        if obj.type == "MESH":
            evaluated = obj.evaluated_get(depsgraph)
            mesh = evaluated.to_mesh()
            mesh.calc_loop_triangles()
            total += len(mesh.loop_triangles)
            evaluated.to_mesh_clear()
    return total


def build():
    options = k.args()
    outdir = options.get("outdir", os.path.join(HERE, "..", "..", "..", "..", "assets", "models", "enemies"))
    k.reset()
    build_machine(materials())
    used = {m.name for o in bpy.context.scene.objects if o.type == "MESH" for m in o.data.materials}
    print("== ring_machine (3 195): %d triangles, %d materials" % (triangles(), len(used)))
    if "check" in options:
        sheet = options["check"]
        k.check_silhouette(os.path.join(sheet, "enemy_3.png") if os.path.isdir(sheet) else sheet, 195)
    bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
    path = os.path.join(outdir, "ring_machine.glb")
    k.export(path)
    print("%s: %d bytes" % (path, os.path.getsize(path)))
    if "preview" in options:
        k.preview(options["preview"] + "ring_machine")


if __name__ == "__main__":
    build()
