"""EYESPY's flying ears (sheet 5 sprites 284 and 245, 2x2: a 19 x 26 ear in the 24 x 28 cell; sky layer, 80 of
each: EYESPY, DELI RUIN, GLACIER; enemies 345 and 347, animations 284 999 and 245 999: no other frames),
polished (2026-10-19; they replace wave3_l.py's ear_left / ear_right, shapeless lumps). models.cfg: sprite 5
284 ear_left yaw=0, sprite 5 245 ear_right yaw=0.

The two sprites are mirror images, pixel for pixel (245 is 284 turned over left to right; --check counts the
pixels that differ): ear_left (284) is built and ear_right is its mirror image across the sprite's middle
(x = 0).

As the 4x upscale draws ear_left: a big tan ear (the sprite's ramp 1: 0x1a skin, 0x1b-0x1e where it catches
the light, 0x13-0x16 in its hollows), wide at its top left and narrowing down to the lobe at its bottom right,
the face it belongs to off to the right. A fleshy rolled rim, the helix, runs round it from the lobe up the
left side, over the top and down the right side to about row 12, a dark groove (the scapha) inside it along
the top and the left. Inside, a Y-shaped ridge (the antihelix): its stem rises from a knob above the lobe (the
antitragus, row 19) up the middle to row 9, where it forks into an arm up to the left and one up to the right,
a shallow hollow (the fossa) between them. To the right of the stem the bowl of the concha sinks in (columns
13-19 of rows 9-17) to the dark ear canal, a knob (the tragus) on the bowl's right rim in front of it (row
15-16); below them the fleshy lobe (rows 21-26).

The ear is one solid: its front a relief over the sprite's outline (the rim, the ridges, the hollows as smooth
bumps and bowls on a gently domed plate), its edge rounding over all round into a rounded back, so the game's
slanted view sees a thick fleshy ear, not a cut-out. The skin is painted in the sprite's shades along smooth
borders: lighter on the crests, darker in the grooves, the bowl and the canal.

Origin at the sprite's centre (pixel 12, 14); +Y up the sprite, +Z towards the camera; the game centres sky
objects in height.

Replaces wave3_l.py's ear_left and ear_right (its MODELS entries "ear_right" and "ear_left" and the art they
use, EAR_RIGHT / EAR_LEFT): remove them so that they don't overwrite these models.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouettes
against enemy_5.png, and the mirror check), --preview <prefix>, --only <name,...>.
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
from polish_ring_machine import Region, ccw, chaikin, resample, round_edge  # noqa: E402
from polish_sphere_nozzle import smoothstep, split_along  # noqa: E402

MODELS = [("ear_left", 284, False), ("ear_right", 245, True)]  # name, sprite, mirrored


def px(c, r):
    """A point given as (column, row) of the sprite's pixel grid (its corners: column 12, row 14 is the
    sprite's centre) in model coordinates."""
    return (c - 12.0, 14.0 - r)


# The outline, a third of a pixel inside the sprite's dark outline pixels (columns and rows of the pixel
# grid's corners), smoothed through.
OUTLINE = [(11.0, 1.25), (12.8, 1.3), (14.7, 2.2), (15.8, 3.2), (16.8, 4.2), (17.8, 5.2), (18.7, 6.2), (19.6, 7.6),
           (20.4, 9.2), (20.7, 11.0), (20.7, 14.0), (20.7, 17.0), (20.7, 20.0), (20.6, 21.4), (20.2, 22.7),
           (19.6, 23.8), (18.7, 24.8), (17.6, 25.7), (16.4, 26.4), (15.0, 26.6), (13.8, 26.2), (12.6, 25.4),
           (11.5, 24.4), (10.7, 23.4), (10.2, 22.4), (9.5, 21.2), (8.7, 19.7), (7.6, 18.4), (6.5, 17.3), (5.5, 16.3),
           (4.6, 15.1), (4.0, 14.0), (3.2, 12.9), (2.6, 11.9), (2.3, 10.8), (2.3, 9.4), (2.6, 8.4), (3.1, 7.3),
           (3.5, 6.2), (4.3, 5.2), (5.3, 4.2), (6.3, 3.2), (7.4, 2.2), (9.2, 1.4)]

# Heights: the outline, the plate inside it, the back's deepest point; the front rounds over within EDGE_ROUND
# of the outline, the back within BACK_ROUND.
EDGE_Z, PLATE_Z, BACK_Z = 0.0, 1.9, -1.9
EDGE_ROUND, BACK_ROUND = 1.0, 3.2
PLATE_DOME = 0.5    # the plate bulges this much more in its middle (DOME_AT, a gaussian DOME_SIZE wide)
DOME_AT, DOME_SIZE = (11.5, 12.0), 7.0

# Positions round the ear are measured as the angle (degrees) round CENTRE, counter-clockwise, from
# ANGLE_ZERO (the lobe's lower right): about 5 at the lobe's right, 70 on the right side at row 11, 155 at the
# top, 227 on the left at row 11, 278 at the lower left (row 17), 313 where the lobe begins.
CENTRE = (12.0, 13.0)
ANGLE_ZERO = -60.0
# The helix: its crest HELIX_AT from the outline, HELIX_WIDTH either side, HELIX_HEIGHT above the plate; it
# runs from HELIX_FROM (the right side, fading in over the first range) to HELIX_TO (into the lobe).
HELIX_AT, HELIX_WIDTH, HELIX_HEIGHT = 1.55, 1.45, 1.6
HELIX_FROM, HELIX_TO = (44.0, 66.0), (282.0, 306.0)
# The scapha, the groove inside the helix: its middle SCAPHA_AT from the outline, its half-width and depth;
# along the top and the left (fading in and out over the ranges).
SCAPHA_AT, SCAPHA_WIDTH, SCAPHA_DEPTH = 4.1, 1.15, 1.0
SCAPHA_FROM, SCAPHA_TO = (84.0, 120.0), (255.0, 284.0)
# The antihelix: polylines (column, row) with the ridge's height and half-width at either end: the stem up
# from the antitragus, the upper arm (superior crus) up to the left, the lower arm (inferior crus) to the
# right over the concha.
ANTIHELIX = [
    ([(14.6, 19.3), (13.0, 17.7), (11.8, 15.6), (11.2, 12.6), (10.9, 10.0), (10.9, 9.0)], (1.1, 1.35), (1.95, 1.65)),
    ([(10.9, 9.0), (10.4, 7.6), (9.9, 6.2), (9.5, 5.4)], (1.3, 0.5), (1.5, 1.05)),
    ([(10.9, 9.0), (12.5, 8.8), (14.2, 8.4), (15.9, 7.6)], (1.25, 0.45), (1.35, 0.95)),
]
# Bowls and knobs: (column, row) of the middle, half-sizes (columns, rows), depth (bowls) or height (knobs).
FOSSA = ((12.7, 6.7), (1.9, 1.35), 0.85)
CONCHA = ((15.5, 13.0), (2.95, 4.65), 2.5)
CANAL = ((16.6, 14.8), (1.9, 1.8), 1.0)
TRAGUS = ((18.5, 16.4), (1.85, 2.05), 1.6)
ANTITRAGUS = ((15.2, 19.4), (2.1, 1.5), 1.0)
LOBE = ((15.6, 23.0), (4.0, 3.4), 0.45)
MIN_THICKNESS = 0.55  # the front never comes closer to the back than this

# The colours' borders: crests above RIDGE (fraction of a ridge's or knob's height), grooves deeper than
# GROOVE and GROOVE_DEEP (fractions of the scapha's or the fossa's depth), the bowl deeper than BOWL and
# HOLLOW (of its depth: its walls shade darker towards its floor), the canal deeper than DEEP.
RIDGE, GROOVE, GROOVE_DEEP, BOWL, HOLLOW, DEEP = 0.45, 0.4, 0.78, 0.1, 0.4, 0.42
SPACING, BACK_SPACING = 0.36, 1.3


# --- Fields ---------------------------------------------------------------------------------------

def bump(q):
    """A smooth bump: 1 at q = 0 falling to 0 at q = 1 (q a squared normalized distance)."""
    return (1.0 - q) ** 2 if q < 1.0 else 0.0


def ellipse_q(x, y, spec):
    (c, r), (hx, hy), _ = spec
    cx, cy = px(c, r)
    return ((x - cx) / hx) ** 2 + ((y - cy) / hy) ** 2


def polyline_nearest(x, y, points):
    """The distance from (x, y) to a polyline of model points and how far along it (0-1) the nearest point
    lies."""
    lengths = [math.dist(a, b) for a, b in zip(points, points[1:])]
    total = sum(lengths)
    best, best_t, walked = 1e9, 0.0, 0.0
    for (ax, ay), (bx, by), length in zip(points, points[1:], lengths):
        dx, dy = bx - ax, by - ay
        t = max(0.0, min(1.0, ((x - ax) * dx + (y - ay) * dy) / max(dx * dx + dy * dy, 1e-12)))
        d = math.hypot(x - ax - t * dx, y - ay - t * dy)
        if d < best:
            best, best_t = d, (walked + t * length) / total
        walked += length
    return best, best_t


ANTIHELIX_MODEL = [([px(c, r) for c, r in pts], h, w) for pts, h, w in ANTIHELIX]


def angle_round(x, y):
    cx, cy = px(*CENTRE)
    return (math.degrees(math.atan2(y - cy, x - cx)) - ANGLE_ZERO) % 360.0


def along(a, start, end):
    """1 between the ranges start and end (fading in over start, out over end), 0 outside."""
    return smoothstep(start[0], start[1], a) * (1.0 - smoothstep(end[0], end[1], a))


class Fields:
    """The relief's parts at a point (x, y), d from the outline: each a fraction 0-1 of its full size."""

    def __init__(self, x, y, d):
        a = angle_round(x, y)
        self.helix = along(a, HELIX_FROM, HELIX_TO) * math.exp(-((d - HELIX_AT) / HELIX_WIDTH) ** 2)
        self.scapha = along(a, SCAPHA_FROM, SCAPHA_TO) * math.exp(-((d - SCAPHA_AT) / SCAPHA_WIDTH) ** 2)
        self.antihelix, self.antihelix_height = 0.0, 0.0
        for points, (h0, h1), (w0, w1) in ANTIHELIX_MODEL:
            dist, t = polyline_nearest(x, y, points)
            w = w0 + (w1 - w0) * t
            f = math.exp(-(dist / w) ** 2)
            h = (h0 + (h1 - h0) * t) * f
            if h > self.antihelix_height:
                self.antihelix_height, self.antihelix = h, f
        self.fossa = bump(ellipse_q(x, y, FOSSA))
        self.concha = bump(ellipse_q(x, y, CONCHA))
        self.canal = bump(ellipse_q(x, y, CANAL))
        self.tragus = bump(ellipse_q(x, y, TRAGUS))
        self.antitragus = bump(ellipse_q(x, y, ANTITRAGUS))
        self.lobe = bump(ellipse_q(x, y, LOBE))

    def ridge(self):
        return max(self.helix, self.antihelix, self.tragus * 1.1, self.antitragus * 1.1)

    def groove(self):
        return max(self.scapha, self.fossa)


def interior(x, y, d):
    """The front's height inside the rounded edge."""
    f = Fields(x, y, d)
    dx, dy = x - px(*DOME_AT)[0], y - px(*DOME_AT)[1]
    z = PLATE_Z + PLATE_DOME * math.exp(-(dx * dx + dy * dy) / DOME_SIZE ** 2)
    # Ridges merge smoothly where they meet (the helix into the antihelix's arms): the higher one, softened.
    ridge = max(HELIX_HEIGHT * f.helix, f.antihelix_height)
    ridge += 0.25 * min(HELIX_HEIGHT * f.helix, f.antihelix_height)
    z += ridge
    z -= SCAPHA_DEPTH * f.scapha * (1.0 - f.antihelix)
    z -= FOSSA[2] * f.fossa
    z -= CONCHA[2] * f.concha * (1.0 - 0.8 * f.antitragus) * (1.0 - 0.7 * f.tragus)
    z -= CANAL[2] * f.canal
    z += TRAGUS[2] * f.tragus + ANTITRAGUS[2] * f.antitragus + LOBE[2] * f.lobe
    return z


def front(x, y, d):
    z = EDGE_Z + (interior(x, y, d) - EDGE_Z) * round_edge(d, EDGE_ROUND)
    return max(z, back(x, y, d) + MIN_THICKNESS * round_edge(d, EDGE_ROUND))


def back(x, y, d):
    return EDGE_Z - (EDGE_Z - BACK_Z) * round_edge(d, BACK_ROUND)


def paint(x, y, d):
    f = Fields(x, y, d)
    if f.canal > DEEP:
        return "deep"
    if f.tragus < 0.35 and f.antitragus < 0.4:
        if f.concha > HOLLOW:
            return "hollow"
        if f.concha > BOWL:
            return "shade"
    if f.groove() > GROOVE_DEEP:
        return "shade_deep"
    if f.groove() > GROOVE:
        return "shade"
    if f.ridge() > RIDGE:
        return "ridge"
    return "skin"


BORDERS = [
    (lambda x, y, d: Fields(x, y, d).canal, DEEP),
    (lambda x, y, d: Fields(x, y, d).concha, HOLLOW),
    (lambda x, y, d: Fields(x, y, d).concha, BOWL),
    (lambda x, y, d: Fields(x, y, d).groove(), GROOVE),
    (lambda x, y, d: Fields(x, y, d).groove(), GROOVE_DEEP),
    (lambda x, y, d: Fields(x, y, d).ridge(), RIDGE),
]


# --- The solid ------------------------------------------------------------------------------------

def hex_grid(region, boundary, spacing):
    xs = [p[0] for p in boundary]
    ys = [p[1] for p in boundary]
    grid = []
    row_step = spacing * math.sqrt(3) / 2
    for j in range(int((max(ys) - min(ys)) / row_step) + 2):
        y = min(ys) + j * row_step
        shift = spacing / 2 if j % 2 else 0.0
        for i in range(int((max(xs) - min(xs)) / spacing) + 2):
            grid.append((min(xs) + shift + i * spacing, y))
    grid = np.array(grid)
    grid = grid[region.inside(grid)]
    return grid[region.distance(grid) > 0.45 * spacing]


def triangulate(region, loop, inner):
    """A constrained Delaunay triangulation of the closed loop (2D points) and the points inside it:
    (vertices, triangles inside the loop as index triples, the input index each vertex came from or None)."""
    n = len(loop)
    points = [Vector(p) for p in loop] + [Vector(tuple(p)) for p in inner]
    verts, _e, faces, orig, *_ = geometry.delaunay_2d_cdt(points, [(i, (i + 1) % n) for i in range(n)], [], 0, 1e-6)
    tris = [f for f in faces if len(f) == 3]
    centroids = np.array([[sum(verts[i].x for i in f) / 3, sum(verts[i].y for i in f) / 3] for f in tris])
    tris = [f for f, keep in zip(tris, region.inside(centroids)) if keep]
    return verts, tris, [o[0] if o else None for o in orig]


def ear_solid(mats):
    """The ear: the front a relief over the outline, cut along the colours' borders first; the back a coarser
    rounded shell meeting it along the outline."""
    outline = ccw(chaikin([px(c, r) for c, r in OUTLINE], 2))
    region = Region([outline])
    boundary = resample(outline, SPACING)
    verts, tris, _ = triangulate(region, boundary, hex_grid(region, boundary, SPACING))
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
    for field, threshold in BORDERS:
        values = {v: field(v.co.x, v.co.y, 0.0 if v in on_outline else dist(v)) for v in bm.verts}
        for v in split_along(bm, values, threshold):
            if any(len(e.link_faces) == 1 for e in v.link_edges):
                on_outline.add(v)
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    front_faces = list(bm.faces)
    keys = {}
    for f in front_faces:
        c = f.calc_center_median()
        d = sum(0.0 if v in on_outline else dist(v) for v in f.verts) / len(f.verts)
        keys[f] = paint(c.x, c.y, d)
    for v in bm.verts:
        v.co.z = front(v.co.x, v.co.y, 0.0 if v in on_outline else dist(v))

    # The back: the outline's loop (as the front left it) and a coarse grid inside.
    loop_edges = [e for e in bm.edges if len(e.link_faces) == 1]
    nxt = {}
    for e in loop_edges:
        a, b = e.verts
        nxt.setdefault(a, []).append(b)
        nxt.setdefault(b, []).append(a)
    start = loop_edges[0].verts[0]
    loop, previous, v = [start], None, start
    while True:
        following = [w for w in nxt[v] if w is not previous]
        previous, v = v, following[0]
        if v is start:
            break
        loop.append(v)
    back_region = Region([[(v.co.x, v.co.y) for v in loop]])
    inner = hex_grid(back_region, [(v.co.x, v.co.y) for v in loop], BACK_SPACING)
    bverts, btris, borig = triangulate(back_region, [(v.co.x, v.co.y) for v in loop], inner)
    made = {}
    for i, o in enumerate(borig):
        if o is not None and o < len(loop):
            made[i] = loop[o]
        else:
            p = bverts[i]
            made[i] = bm.verts.new((p.x, p.y, back(p.x, p.y, float(region.distance([(p.x, p.y)])[0]))))
    for f in btris:
        try:
            face = bm.faces.new([made[i] for i in reversed(f)])
            keys[face] = "back"
        except ValueError:
            pass
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mesh = bpy.data.meshes.new("ear")
    names = []  # material names (some keys share a material)
    for f in bm.faces:
        name = mats[keys.get(f, "back")].name
        if name not in names:
            names.append(name)
        f.material_index = names.index(name)
    for name in names:
        mesh.materials.append(bpy.data.materials[name])
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new("ear", mesh)
    bpy.context.scene.collection.objects.link(obj)
    return k.smooth(obj, 88)


def materials():
    skin = dict(metallic=0.0, roughness=0.56)
    shade = k.material("ear_shade", palette=0x17, **skin)
    hollow = k.material("ear_hollow", palette=0x15, **skin)
    return {
        "skin": k.material("ear_skin", palette=0x1a, **skin),
        "ridge": k.material("ear_ridge", palette=0x1b, metallic=0.0, roughness=0.5),
        "shade": shade,
        "shade_deep": hollow,   # the grooves' deepest part, the bowl and the back share the hollows' shades
        "hollow": hollow,
        "deep": k.material("ear_canal", palette=0x13, metallic=0.0, roughness=0.6),
        "back": shade,
    }


# --- Build ----------------------------------------------------------------------------------------

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


def mirror_check(sheet):
    """How many pixels of 245 differ from 284 turned over left to right."""
    from sprite_profile import sprite_indices
    a, b = sprite_indices(sheet, 284), sprite_indices(sheet, 245)
    diff = sum(1 for r in range(28) for c in range(24) if a[r][c] != b[r][23 - c])
    print("mirror check: %d pixels of 245 differ from 284 mirrored" % diff)


def build():
    options = k.args()
    outdir = options.get("outdir", os.path.join(HERE, "..", "..", "..", "..", "assets", "models", "enemies"))
    only = options["only"].split(",") if "only" in options else [m[0] for m in MODELS]
    sheet = options.get("check")
    if sheet and os.path.isdir(sheet):
        sheet = os.path.join(sheet, "enemy_5.png")
    if sheet:
        mirror_check(sheet)
    for name, sprite, mirrored in MODELS:
        if name not in only:
            continue
        k.reset()
        ear = ear_solid(materials())
        if mirrored:
            ear.data.transform(Matrix.Scale(-1, 4, (1, 0, 0)))
            ear.data.flip_normals()
            k.recalc_normals(ear)
        zs = [v.co.z for v in ear.data.vertices]
        print("== %s (5 %d): %d triangles, %d materials, z %.2f to %.2f" % (
            name, sprite, triangles(), len(ear.data.materials), min(zs), max(zs)))
        if sheet:
            k.check_silhouette(sheet, sprite)
        bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
        path = os.path.join(outdir, name + ".glb")
        k.export(path)
        print("   %s: %.1f KB" % (name, os.path.getsize(path) / 1024))
        if "preview" in options:
            k.preview(options["preview"] + name)


if __name__ == "__main__":
    build()
