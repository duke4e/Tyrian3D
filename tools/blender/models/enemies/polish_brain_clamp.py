"""BRAINIAC's and GRAVITRON's red brain in its steel clamps (sheet 5 sprite 166, 2x2: the top 15 rows of
the 24 x 28 cell, all 24 columns; static; top layer; enemy 521: 64 in BRAINIAC, 82 in GRAVITRON),
polished (2026-10-18; it replaces wave2_h.py's brain_clamp()). models.cfg: sprite 5 166 brain_clamp
yaw=0.

The levels lay it out in rows across the screen: two to four side by side, 24 pixels apart, at the
same time on the top layer (BRAINIAC's events 108, 500, 584, 1060, 1228 ... as x 72 and 96, 144 and
168, ...), a chain of brains linked by the clamps between them; nothing else is placed against them
(BRAINIAC's big brain, 5 196-276 of wave3_l_parts.py, is the level's boss, elsewhere; the red links,
5 168, stack down the screen on their own). So the sprite's ends are half clamps: its columns 20-23
and the next one's columns 0-3 make one steel bracket, an arch over the seam whose two legs hug the
rounded ends of the brains either side (rows 7-11; the gap between the legs is open).

As the 4x upscale draws it: a mass of glossy red lobes folded together (the sprite's ramp 7: dark
red folds, red lobes, the lobe in the middle brightest), glowing orange along the middle lobe's
upper edge (row 5) and at the foot of the narrow lobe above it (column 10, rows 1-5), a bright
orange eye on the lower left lobe (columns 5-6 of rows 7-8). Blue-grey steel (ramp 6) holds it: the
brackets at the ends, a rail from the left bracket into the brain (row 5) ending in a hook over the
upper left lobe (columns 6-8 of rows 2-5), two rails from the right bracket (rows 5 and 7), and a
strap from the lower one round the bottom of the middle (columns 10-13 of rows 9-14).

The brain is one solid (relief() of polish_ring_machine.py) whose top is the smooth union of its
lobes (ellipsoid caps), so that the folds between them are real creases, painted dark, the lobes'
tops lighter and the glow painted on (its colours cut in along smooth borders); the flesh glows a
little in its own reds, the glow and the eye (a low dome) strongly. The steel parts follow the
brain's surface. The bracket is built whole over the seam at x = 12 and cut there (cut(), as
polish_redjet.py's, keeps the uncut shading): the part left of the seam is this sprite's right
end, the part right of it, moved 24 pixels left, its left end, so that side by side they meet into
one bracket; the rails reaching into the brackets are cut at the sprite's edges too.

Origin at the sprite's centre (pixel 12, 14); +Y up the sprite, +Z towards the camera. Points are
given as (column, row) of the sprite.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <dir with enemy_5.png,
or the sheet itself> (the silhouette), --preview <prefix>, --chain <prefix> (three side by side, as
the levels place them: <prefix>_top.png and _3q.png).
"""
import math
import os
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
from polish_ring_machine import Region, ccw, chaikin, dome, relief, round_edge  # noqa: E402
from polish_sphere_nozzle import smoothstep  # noqa: E402


def px(c, r):
    return (c - 12.0, 14.0 - r)


# The brain's outline (column, row): under the brackets at its ends, its top reaching row 0 at
# columns 9-13, its lower corners rounded, its bottom at row 13.9.
BRAIN = [(2.7, 3.0), (3.0, 1.2), (5.0, 0.8), (8.8, 0.7), (9.3, 0.25), (10.1, 0.02), (12.0, 0.02), (12.8, 0.3),
         (13.5, 0.75), (19.5, 0.8), (21.0, 1.2), (21.3, 3.0), (21.35, 7.0), (21.3, 9.5), (21.1, 11.6), (20.5, 12.8),
         (19.6, 13.7), (14.5, 13.95), (9.5, 13.95), (4.6, 13.7), (3.6, 12.8), (3.0, 11.6), (2.75, 9.5), (2.7, 7.0)]
# The lobes, packed so that only narrow folds part them: (name, column, row, half-width,
# half-height (rows), height).
LOBES = [
    ("UL", 4.9, 3.0, 2.35, 3.05, 3.3),
    ("UC", 10.45, 2.6, 1.95, 3.05, 3.45),
    ("UR", 16.0, 2.8, 4.95, 2.45, 3.2),
    ("MC", 13.0, 6.75, 3.6, 2.25, 3.85),
    ("MR", 18.8, 6.85, 3.0, 2.35, 3.0),
    ("LL", 6.3, 9.3, 3.85, 4.65, 3.8),
    ("LM", 11.8, 11.7, 2.85, 2.65, 3.2),
    ("LR", 17.3, 11.3, 3.85, 3.0, 3.5),
]
FLOOR, BLEND = 1.7, 0.45      # the height between the lobes, how softly they merge
EDGE_Z, EDGE_RIM = -0.6, 1.5  # the outline's height and how far in its rounded edge reaches
BOTTOM = -2.0
FOLD = 0.24                   # where the two highest lobes are this close, a fold (painted dark)
LIGHT = 0.62                  # a lobe's top (above this fraction of its height): lighter
BRIGHT = ("MC", "UC")         # the brightest lobes
# Where the brain glows (the sprite's orange, columns 10-11 of rows 1-5 and row 5 to column 15): two
# strokes (column, row) to (column, row) and their half-widths at either end (widest where they
# meet, at the middle lobe's upper left corner); the hotter core, its inner part.
GLOW = [((10.3, 1.3), (10.45, 4.85), 0.3, 0.68), ((10.45, 5.05), (14.9, 5.15), 0.68, 0.32)]
GLOW_CORE = 0.45

# The bracket over the seam (x' about the seam, row): a block over the top, two legs down either
# side of the brains' ends, the gap between them open.
BRACKET = [(-4.1, 0.0), (4.1, 0.0), (4.0, 2.0), (3.75, 4.0), (3.45, 5.8), (3.2, 7.5), (3.1, 9.5), (2.9, 11.0),
           (2.45, 11.75), (1.95, 11.45), (1.75, 9.5), (1.35, 7.6), (0.65, 6.75), (0.0, 6.55), (-0.65, 6.75),
           (-1.35, 7.6), (-1.75, 9.5), (-1.95, 11.45), (-2.45, 11.75), (-2.9, 11.0), (-3.1, 9.5), (-3.2, 7.5),
           (-3.45, 5.8), (-3.75, 4.0), (-4.0, 2.0)]
BRACKET_TOP, LEG_TOP, BRACKET_RIM, BRACKET_BOTTOM = 4.6, 3.7, 1.0, -2.4
# The rails and the hook (paths of (column, row)), their radius and how far above the brain's
# surface their middle lies.
RAILS = [
    [(0.0, 5.45), (3.0, 5.45), (6.5, 5.4)],
    [(6.5, 5.5), (6.55, 4.0), (6.6, 2.5), (7.3, 2.35), (9.1, 2.4)],  # the hook
    [(15.6, 5.45), (19.0, 5.45), (24.0, 5.45)],
    [(15.4, 7.35), (19.0, 7.4), (24.0, 7.4)],
]
RAIL_RADIUS, RAIL_LIFT = 0.58, 0.3
# The strap from the lower right rail round the bottom of the middle (column, row): it lies on the
# brain (smoothed, STRAP_LIFT above it) and bends down over its lower edge.
STRAP = [(9.8, 14.65), (13.75, 14.65), (13.75, 9.8), (17.1, 9.8), (17.1, 7.4), (15.95, 7.4), (15.95, 8.7),
         (9.8, 8.7)]
STRAP_LIFT = 0.5
EYE = (5.55, 7.55, 1.1)  # the eye on the lower left lobe: column, row, radius


# --- The brain's surface --------------------------------------------------------------------------

def lobe_heights(x, y):
    """Each lobe's (height at (x, y), name, its rise above the floor there as a fraction of its
    height, where along its half-height (y) the point lies): ellipsoid caps over the floor."""
    out = []
    for name, c, r, hw, hh, h in LOBES:
        cx, cy = px(c, r)
        q = ((x - cx) / hw) ** 2 + ((y - cy) / hh) ** 2
        rise = math.sqrt(max(0.0, 1.0 - q))
        out.append((FLOOR + (h - FLOOR) * rise, name, rise, (y - cy) / hh))
    return out


def smax(a, b, k_):
    h = max(k_ - abs(a - b), 0.0) / k_
    return max(a, b) + h * h * k_ * 0.25


def flesh_z(x, y):
    z = FLOOR
    for h, *_ in lobe_heights(x, y):
        z = smax(z, h, BLEND)
    return z


def fold(x, y):
    """How far the highest lobe stands above the next one (0 along a fold)."""
    heights = sorted(lobe_heights(x, y), reverse=True)
    if heights[1][0] <= FLOOR + 0.15:
        return 9.0
    return heights[0][0] - heights[1][0]


def top_lobe(x, y):
    return max(lobe_heights(x, y))


def glow(x, y):
    """1 on the glowing strokes' middle lines, 0 at their edges (negative outside)."""
    best = -1.0
    for (c0, r0), (c1, r1), w0, w1 in GLOW:
        ax, ay = px(c0, r0)
        bx, by = px(c1, r1)
        dx, dy = bx - ax, by - ay
        t = max(0.0, min(1.0, ((x - ax) * dx + (y - ay) * dy) / (dx * dx + dy * dy)))
        dist = math.hypot(x - ax - t * dx, y - ay - t * dy)
        best = max(best, 1.0 - dist / (w0 + (w1 - w0) * t))
    return best


class Brain:
    def __init__(self):
        self.outline = ccw(chaikin([px(c, r) for c, r in BRAIN], 2))
        self.region = Region([self.outline])

    def top(self, x, y, d=None):
        if d is None:
            d = float(self.region.distance([(x, y)])[0])
            if not self.region.inside([(x, y)])[0]:
                return EDGE_Z
        return EDGE_Z + (flesh_z(x, y) - EDGE_Z) * round_edge(d, EDGE_RIM)


def brain(mats, b):
    def paint(x, y, d):
        g = glow(x, y)
        if g > GLOW_CORE:
            return "glow_core"
        if g > 0.0:
            return "glow"
        if d < 0.55 or fold(x, y) < FOLD:
            return "flesh_dark"
        _, name, rise, _ = top_lobe(x, y)
        if rise > LIGHT:
            return "flesh_bright" if name in BRIGHT else "flesh_light"
        return "flesh"

    borders = [(lambda x, y, d: d, 0.55), (lambda x, y, d: fold(x, y), FOLD),
               (lambda x, y, d: top_lobe(x, y)[2], LIGHT), (lambda x, y, d: glow(x, y), 0.0),
               (lambda x, y, d: glow(x, y), GLOW_CORE)]
    return relief("brain", [b.outline], lambda x, y, d: b.top(x, y, d), mats, paint=paint, side="flesh_dark",
                  bottom=BOTTOM, spacing=0.5, borders=borders, smooth_angle=55)


# --- The steel ------------------------------------------------------------------------------------

def bracket(mats):
    """The bracket over the seam at x = 12, whole (cut into the sprite's two ends afterwards)."""
    poly = ccw(chaikin([(12.0 + x, 14.0 - r) for x, r in BRACKET], 2))

    def height(x, y, d):
        top = LEG_TOP + (BRACKET_TOP - LEG_TOP) * smoothstep(px(0, 8.0)[1], px(0, 5.8)[1], y)
        return 1.0 + (top - 1.0) * round_edge(d, BRACKET_RIM)

    def paint(x, y, d):
        return "steel" if d > 0.3 else "steel_dark"

    return relief("bracket", [poly], height, mats, paint=paint, side="steel_dark", bottom=BRACKET_BOTTOM,
                  spacing=0.3, borders=[(lambda x, y, d: d, 0.3)], band=1.3)


def rail(name, points, mats, b):
    """A round bar along the points, lying on the brain (its middle RAIL_LIFT above the surface)."""
    path = []
    for (c0, r0), (c1, r1) in zip(points, points[1:]):
        p0, p1 = Vector(px(c0, r0)), Vector(px(c1, r1))
        n = max(1, int((p1 - p0).length / 0.4))
        path += [p0.lerp(p1, i / n) for i in range(n)]
    path.append(Vector(px(*points[-1])))
    zs = [max(b.top(p.x, p.y), 1.2) + RAIL_LIFT for p in path]
    zs = [sum(zs[max(0, i - 2):i + 3]) / len(zs[max(0, i - 2):i + 3]) for i in range(len(zs))]  # smoothed
    rings = []
    for i, (p, z) in enumerate(zip(path, zs)):
        a, c = path[max(i - 1, 0)], path[min(i + 1, len(path) - 1)]
        t = (c - a).normalized()
        side = Vector((-t.y, t.x, 0.0))
        centre = Vector((p.x, p.y, z))
        rings.append([centre + side * math.cos(2 * math.pi * j / 8) * RAIL_RADIUS +
                      Vector((0, 0, 1)) * math.sin(2 * math.pi * j / 8) * RAIL_RADIUS * 0.85 for j in range(8)])
    first = Vector((path[0].x, path[0].y, zs[0]))
    last = Vector((path[-1].x, path[-1].y, zs[-1]))
    obj = k.loft(name, rings, mats["steel"], start_point=first - (path[1] - path[0]).normalized().to_3d() * 0.4,
                 end_point=last + (path[-1] - path[-2]).normalized().to_3d() * 0.4)
    return k.smooth(obj, 50)


def strap(mats, b):
    """The strap: a plate lying on the brain, the brain's surface under it averaged over a few
    pixels so that it lies smooth over the folds, bending down over the brain's lower edge."""
    poly = ccw(chaikin([px(c, r) for c, r in STRAP], 1))

    def under(x, y):
        samples = [b.top(x + dx, y + dy) for dx in (-1.2, 0.0, 1.2) for dy in (-1.2, 0.0, 1.2)]
        return max(sum(samples) / len(samples), b.top(x, y))

    return relief("strap", [poly], lambda x, y, d: under(x, y) + STRAP_LIFT * (0.4 + 0.6 * round_edge(d, 0.4)),
                  mats, paint=lambda x, y, d: "steel" if d > 0.3 else "steel_dark", side="steel_dark",
                  bottom=BOTTOM + 0.5, spacing=0.42, borders=[(lambda x, y, d: d, 0.3)])


# --- The eye --------------------------------------------------------------------------------------

def eye(mats, b):
    """The glowing eye: a low round dome set into the lower left lobe, white-hot in its middle."""
    c, r, radius = EYE
    x, y = px(c, r)

    def core(px_, py_, pz):
        return math.hypot(px_ - x, py_ - y) / radius

    return dome("eye", (x, y), (radius, radius * 0.95), b.top(x, y) - 0.45, 0.8, mats,
                lambda px_, py_, pz: "eye" if core(px_, py_, pz) < 0.6 else "eye_rim", [(core, 0.6)], rings=5,
                segments=24, skirt=0.5)


# --- Cutting at the seam (as polish_redjet.py's cut(), which can't be imported: it builds on import) --

def barycentric(p, a, b, c):
    v0, v1, v2 = b - a, c - a, p - a
    d00, d01, d11 = v0.dot(v0), v0.dot(v1), v1.dot(v1)
    d20, d21 = v2.dot(v0), v2.dot(v1)
    den = d00 * d11 - d01 * d01
    if abs(den) < 1e-12:
        return (1 / 3, 1 / 3, 1 / 3)
    v = (d11 * d20 - d01 * d21) / den
    w = (d00 * d21 - d01 * d20) / den
    weights = [max(0.0, 1 - v - w), max(0.0, v), max(0.0, w)]
    total = sum(weights) or 1.0
    return [x / total for x in weights]


def cut(source, x0, x1, cap_mat):
    """The part of an object between x0 and x1, its cuts closed with flat caps of cap_mat, its
    normals those of the uncut object (so that the shading runs on across the cut)."""
    mesh = source.data
    mesh.calc_loop_triangles()
    verts = [v.co.copy() for v in mesh.vertices]
    tris = [(tuple(t.vertices), tuple(t.loops)) for t in mesh.loop_triangles]
    corner = [n.vector.copy() for n in mesh.corner_normals]
    bvh = BVHTree.FromPolygons(verts, [t[0] for t in tris])

    def shading(co, towards):
        _, _, index, _ = bvh.find_nearest(co + (towards - co) * 0.02)
        if index is None:
            return None
        (ia, ib, ic), (la, lb, lc) = tris[index]
        w = barycentric(co, verts[ia], verts[ib], verts[ic])
        n = corner[la] * w[0] + corner[lb] * w[1] + corner[lc] * w[2]
        return n.normalized() if n.length > 1e-8 else None

    obj = source.copy()
    obj.data = source.data.copy()
    bpy.context.scene.collection.objects.link(obj)
    if cap_mat.name not in obj.data.materials:
        obj.data.materials.append(cap_mat)
    cap_index = list(obj.data.materials).index(cap_mat)
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    caps = set()
    for co, no in (((x0, 0, 0), (-1, 0, 0)), ((x1, 0, 0), (1, 0, 0))):
        result = bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-6, plane_co=co,
                                        plane_no=no, clear_outer=True)
        edges = [e for e in result["geom_cut"] if isinstance(e, bmesh.types.BMEdge) and e.is_valid]
        open_edges = [e for e in edges if len(e.link_faces) == 1]
        if open_edges:
            filled = bmesh.ops.holes_fill(bm, edges=open_edges, sides=0)
            if filled["faces"]:
                caps |= set(bmesh.ops.triangulate(bm, faces=filled["faces"])["faces"])
    caps = {f for f in caps if f.is_valid}
    for f in caps:
        f.material_index = cap_index
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.faces.index_update()
    cap_ids = {f.index for f in caps}
    bm.to_mesh(obj.data)
    bm.free()
    out = obj.data
    normals = []
    for poly in out.polygons:
        for li in poly.loop_indices:
            n = None if poly.index in cap_ids else shading(out.vertices[out.loops[li].vertex_index].co, poly.center)
            normals.append(tuple(n if n is not None else poly.normal))
    out.normals_split_custom_set(normals)
    return obj


# --- Build ----------------------------------------------------------------------------------------

def materials():
    pal = k.level_palette()
    return {
        "flesh_dark": k.material("brainc_flesh_dark", palette=0x70, metallic=0.1, roughness=0.35),
        "flesh": k.material("brainc_flesh", palette=0x72, metallic=0.1, roughness=0.28, emission=pal[0x72],
                            emission_strength=0.2),
        "flesh_light": k.material("brainc_flesh_light", palette=0x74, metallic=0.1, roughness=0.24,
                                  emission=pal[0x73], emission_strength=0.22),
        "flesh_bright": k.material("brainc_flesh_bright", palette=0x75, metallic=0.1, roughness=0.22,
                                   emission=pal[0x74], emission_strength=0.3),
        "glow": k.material("brainc_glow", palette=0x77, roughness=0.25, emission=pal[0x77], emission_strength=0.9),
        "glow_core": k.material("brainc_glow_core", palette=0x7a, roughness=0.25, emission=pal[0x79],
                                emission_strength=1.3),
        "eye_rim": k.material("brainc_eye_rim", palette=0x78, roughness=0.25, emission=pal[0x77],
                              emission_strength=1.2),
        "eye": k.material("brainc_eye", palette=0x7b, roughness=0.2, emission=pal[0x7b], emission_strength=1.8),
        "steel": k.material("brainc_steel", palette=0x6a, metallic=0.45, roughness=0.25),
        "steel_dark": k.material("brainc_steel_dark", palette=0x66, metallic=0.45, roughness=0.35),
    }


def build_clamp(mats):
    b = Brain()
    brain(mats, b)
    eye(mats, b)
    for i, points in enumerate(RAILS):
        rail(f"rail{i}", points, mats, b)
    strap(mats, b)
    whole = bracket(mats)
    # Cut the bracket at the seam: its left part is this sprite's right end, its right part (moved
    # 24 pixels left) its left end.
    right_end = cut(whole, -100.0, 12.0, mats["steel_dark"])
    left_end = cut(whole, 12.0, 100.0, mats["steel_dark"])
    left_end.data.transform(Matrix.Translation((-24.0, 0.0, 0.0)))
    right_end.name, left_end.name = "bracket_right", "bracket_left"
    bpy.data.objects.remove(whole)
    # The rails reaching into the brackets end inside them: cut at the sprite's edges too.
    for obj in [o for o in bpy.context.scene.objects if o.type == "MESH" and o.name.startswith("rail")]:
        corners = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
        if max(c.x for c in corners) > 12.0 or min(c.x for c in corners) < -12.0:
            part = cut(obj, -12.0, 12.0, mats["steel_dark"])
            name = obj.name
            bpy.data.objects.remove(obj)
            part.name = name


def triangles(objects=None):
    depsgraph = bpy.context.evaluated_depsgraph_get()
    total = 0
    for obj in objects or bpy.context.scene.objects:
        if obj.type == "MESH":
            evaluated = obj.evaluated_get(depsgraph)
            mesh = evaluated.to_mesh()
            mesh.calc_loop_triangles()
            total += len(mesh.loop_triangles)
            evaluated.to_mesh_clear()
    return total


def chain_preview(prefix):
    """Three side by side, as the levels place them (renders <prefix>_top.png and _3q.png)."""
    meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    copies = []
    for dx in (-24.0, 24.0):
        for obj in meshes:
            copy = obj.copy()
            copy.data = obj.data.copy()
            bpy.context.scene.collection.objects.link(copy)
            copy.location.x += dx
            copies.append(copy)
    k.preview(prefix, size=(72, 28), scale=8)
    for obj in copies:
        bpy.data.objects.remove(obj)
    for obj in [o for o in bpy.context.scene.objects if o.type in ("CAMERA", "LIGHT")]:
        bpy.data.objects.remove(obj)


def build():
    options = k.args()
    outdir = options.get("outdir", os.path.join(HERE, "..", "..", "..", "..", "assets", "models", "enemies"))
    k.reset()
    build_clamp(materials())
    used = {m.name for o in bpy.context.scene.objects if o.type == "MESH" for m in o.data.materials}
    print("== brain_clamp (5 166): %d triangles, %d materials" % (triangles(), len(used)))
    if "check" in options:
        sheet = options["check"]
        k.check_silhouette(os.path.join(sheet, "enemy_5.png") if os.path.isdir(sheet) else sheet, 166)
    bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
    path = os.path.join(outdir, "brain_clamp.glb")
    k.export(path)
    print("%s: %d bytes" % (path, os.path.getsize(path)))
    if "chain" in options:
        chain_preview(options["chain"])
    if "preview" in options:
        k.preview(options["preview"] + "brain_clamp")


if __name__ == "__main__":
    build()
