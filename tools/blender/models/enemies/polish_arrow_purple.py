"""The purple arrowhead of HARVEST and LAVA RUN (sheet 5 sprite 1, 2x2: a 17 x 24 shield in the 24 x 28
cell; static; sky and top (HARVEST: 95 of them), ground (2)), polished (2026-10-18; it replaces
later_episodes.py's arrow_purple (in ships()), a flat lilac plate with a ridge). models.cfg: sprite
5 1 arrow_purple yaw=0.

As the 4x upscale draws it: a faceted purple gem pointing up the screen, a sharp ridge down its
middle from the point (row 0) to its lower tip (row 18), its left facets lit lilac, its right ones
in deep shadow: the arrowhead widens to shoulders (columns 4-20 of rows 7-10), under which the body
narrows to a keel (columns 8-16 of rows 11-14) that tapers to the lower tip. Round the keel hangs a
crescent, a band curving from under the left shoulder down round the tip and up under the right
one (columns 6-18 of rows 11-22), glowing yellow-orange at the bottom and darkening to deep red and
magenta up its arms, as an engine's exhaust slot. A near-black outline holds it all (the sprite's
0x20 border and the gaps between the gem and the crescent).

The model: a dark backing shield over the whole outline (rounded edges; relief() of
polish_ring_machine.py), the gem standing on it as a faceted solid (a roof of planes over its
outline: one slope either side of the sharp ridge, falling to the point and to the tip, so that
each side reads as one facet as in the sprite; walls drop where the outline steps in under the
shoulders, the sprite's dark line there; the sprite's light painted on, as the game's sun comes
from the same side: left of the ridge lilac, right of it deep purple), and the crescent as a
flattened tube set into the backing, glowing in the sprite's ramp 15: hottest along the top of the
band a little inside its middle and towards the bottom, deep red and magenta at its outer rim and
up its arms (the shades' borders cut in along smooth lines).

The sprite is symmetric about its column 12.5 (x 0.5 here): the model is built about x = 0 and moved
there (AXIS_X). Points are given as (column, row) of the sprite. Origin at the sprite's centre
(pixel 12, 14); +Y up the sprite, +Z towards the camera.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <dir with enemy_5.png,
or the sheet itself> (the silhouette), --preview <prefix>.
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
from polish_ring_machine import ccw, chaikin, px, relief, round_edge  # noqa: E402
from polish_sphere_nozzle import split_along  # noqa: E402

AXIS_X = 0.5

# The backing: the sprite's whole outline, its left half from the top point down to the bottom
# middle (column, row), from the upscale's edge.
BACKING_LEFT = [(12.5, 0.05), (11.6, 0.9), (10.3, 2.1), (9.3, 3.1), (8.3, 4.1), (7.4, 4.7), (6.5, 5.3), (5.6, 6.0),
                (4.8, 6.6), (4.25, 7.1), (4.0, 7.65), (4.0, 10.1), (4.2, 10.6), (4.25, 11.6), (4.6, 12.3),
                (4.85, 13.3), (5.0, 14.1), (5.05, 16.1), (5.25, 17.0), (5.4, 17.9), (5.8, 18.7), (6.3, 19.6),
                (6.9, 20.3), (7.6, 21.0), (8.3, 21.8), (9.2, 22.6), (10.1, 23.15), (11.2, 23.65)]
BACKING_TOP, BACKING_BOTTOM, BACKING_RIM = 0.8, -1.2, 0.9

# The gem: its outline's left half (the point, the shoulder's corners, where the shoulder's
# underside meets the keel, the keel's lower corner and the lower tip). Its top is a roof of planes:
# either side of the ridge (x = 0) one slope, the ridge at RIDGE_HEIGHT between the rows UPPER_ROW
# (the shoulders' corners) and LOWER_ROW (the shoulders' underside), falling to the point and to
# the tip (the planes there slope down the ridge so that they meet the outline at EDGE). Where the
# outline steps in under the shoulders and along the keel the roof stands higher than EDGE: straight
# walls drop from it there (the sprite's dark line under the shoulders). WALL: how far the walls
# reach below EDGE (into the backing); CHAMFER: the edges' small bevel (depth, width).
GEM_LEFT = [(12.5, 0.55), (4.85, 7.4), (4.75, 10.75), (7.95, 10.95), (8.0, 14.0), (12.5, 18.45)]
RIDGE_HEIGHT, EDGE, WALL = 5.9, 1.25, 0.9
UPPER_ROW, LOWER_ROW = 7.4, 10.8
CHAMFER = (0.3, 0.35)

# The crescent: its middle line (column, row) from the left arm's tip round the bottom to the right
# one's, its half-width at the tips and at the bottom, its half-height and its middle's height.
CRESCENT_LEFT = [(6.45, 11.7), (6.55, 13.4), (6.9, 15.3), (7.6, 16.9), (8.7, 18.3), (10.3, 19.45), (12.5, 19.95)]
CRESCENT_WIDTH, CRESCENT_HEIGHT, CRESCENT_Z = (0.6, 1.35), 0.62, 0.95
# The glow: strongest along the top of the band, a little inside its middle (CORE: where across
# the band, -1 inner edge to 1 outer edge; CORE_WIDTH), and towards the bottom (bottomness, 0 at
# the tips, 1 at the bottom, to the power GLOW_POWER); the borders between the shades.
CORE, CORE_WIDTH, GLOW_POWER = -0.15, 0.55, 1.3
GLOW_BANDS = (0.12, 0.3, 0.55, 0.78)
SHADES = ("deep", "dark", "red", "warm", "hot")


def mirrored_path(left):
    """A path from the left half's points: the left ones, then their mirror images back up."""
    return left + [(25.0 - c, r) for c, r in reversed(left[:-1])]


def gem(mats):
    """The faceted gem: the roof of planes over its outline (relief() with the ridge and the two
    creases across cut in, so that the facets meet along straight lines), flat shaded, with the
    sprite's light painted on (the game's sun comes from the same side): the facets left of the
    ridge lilac, those right of it deep purple, the walls dark."""
    left = [px(c, r) for c, r in GEM_LEFT]
    outline = ccw(left + [(-x, y) for x, y in reversed(left[1:-1])])
    y_top, y_tip = left[0][1], left[-1][1]
    y_upper, y_lower = px(0, UPPER_ROW)[1], px(0, LOWER_ROW)[1]
    rise = RIDGE_HEIGHT - EDGE
    slope = rise / -min(x for x, _ in left)               # across: from the ridge to the shoulders
    slope_top = rise / (y_top - y_upper)                  # down the ridge to the point
    slope_tip = rise / (y_lower - y_tip)                  # down the ridge to the tip

    def height(x, y, d):
        ridge = min(RIDGE_HEIGHT, EDGE + slope_top * (y_top - y), EDGE + slope_tip * (y - y_tip))
        return ridge - slope * abs(x) - CHAMFER[0] * max(0.0, 1.0 - d / CHAMFER[1]) ** 2

    def paint(x, y, d):
        return "gem" if x < 0 else "gem_dark"

    borders = [(lambda x, y, d: x, 0.0), (lambda x, y, d: y, y_upper), (lambda x, y, d: y, y_lower)]
    return relief("gem", [outline], height, mats, paint=paint, side="gem_under", bottom=EDGE - WALL,
                  spacing=0.4, borders=borders, smooth_angle=20.0)


def backing(mats):
    left = [px(c, r) for c, r in BACKING_LEFT]
    right = [(-x, y) for x, y in reversed(left[1:])]
    outline = ccw(chaikin(left + [(0.0, px(0, 23.85)[1])] + right, 1))
    return relief("backing", [outline], lambda x, y, d: BACKING_TOP - 0.9 + 0.9 * round_edge(d, BACKING_RIM), mats,
                  paint=lambda x, y, d: "backing", side="backing", bottom=BACKING_BOTTOM, spacing=0.5, band=1.3)


def crescent(mats, segments=16):
    """The glowing crescent: a flattened tube along its middle line, its tips rounded off, its
    shades by the glow (GLOW_BANDS)."""
    path = [Vector((*px(c, r), CRESCENT_Z)) for c, r in mirrored_path(CRESCENT_LEFT)]
    # A smooth, evenly spaced middle line.
    dense = []
    for i in range(len(path) - 1):
        p0, p1 = path[max(i - 1, 0)], path[i]
        p2, p3 = path[i + 1], path[min(i + 2, len(path) - 1)]
        for s in range(8):
            t = s / 8
            dense.append(0.5 * (2 * p1 + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t +
                                (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    dense.append(path[-1])
    lengths = [0.0]
    for a, b in zip(dense, dense[1:]):
        lengths.append(lengths[-1] + (b - a).length)
    total = lengths[-1]
    count = 64
    points, j = [], 0
    for i in range(count + 1):
        target = total * i / count
        while j < len(dense) - 2 and lengths[j + 1] < target:
            j += 1
        f = (target - lengths[j]) / max(lengths[j + 1] - lengths[j], 1e-9)
        points.append(dense[j].lerp(dense[j + 1], min(1.0, f)))
    rings, along = [], []
    for i, p in enumerate(points):
        a, b = points[max(i - 1, 0)], points[min(i + 1, count)]
        tangent = (b - a).normalized()
        side = Vector((tangent.y, -tangent.x, 0.0))  # outwards (the path runs counter-clockwise)
        t = i / count
        bottomness = 1.0 - abs(2 * t - 1.0)  # 0 at the tips, 1 at the bottom
        w = CRESCENT_WIDTH[0] + (CRESCENT_WIDTH[1] - CRESCENT_WIDTH[0]) * math.sin(0.5 * math.pi * bottomness) ** 1.5
        end = min(i, count - i)
        shrink = math.sqrt(max(0.0, 1 - (1 - end / 3) ** 2)) if end < 3 else 1.0  # the rounded tips
        ring = []
        for s in range(segments):
            ang = 2 * math.pi * s / segments
            c, sn = math.cos(ang), math.sin(ang)
            ring.append(p + side * (w * shrink * math.copysign(abs(c) ** (2 / 2.6), c)) +
                        Vector((0, 0, CRESCENT_HEIGHT * max(shrink, 0.35) * math.copysign(abs(sn) ** (2 / 2.6), sn))))
        rings.append(ring)
        along.append(bottomness)
    obj = k.loft("crescent", rings, None, start_point=points[0], end_point=points[-1])
    # The glow at each vertex (the loft's vertices: ring by ring, then the two end points), its
    # shades' borders cut in so that they run smoothly, then each face's shade by its glow.
    n = segments
    values = []
    for i in range(len(rings)):
        for s in range(n):
            ang = 2 * math.pi * s / n
            across, up = math.cos(ang), math.sin(ang)
            values.append(along[i] ** GLOW_POWER * math.exp(-((across - CORE) / CORE_WIDTH) ** 2) *
                          (0.35 + 0.65 * max(0.0, up)))
    values += [0.0, 0.0]
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.verts.ensure_lookup_table()
    field = {v: values[v.index] for v in bm.verts}
    for t in GLOW_BANDS:
        split_along(bm, field, t)
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    keys = []
    for f in bm.faces:
        glow = sum(field[v] for v in f.verts) / len(f.verts)
        keys.append(SHADES[sum(glow > t for t in GLOW_BANDS)])
    bm.to_mesh(obj.data)
    bm.free()
    names = []
    for poly, key in zip(obj.data.polygons, keys):
        if key not in names:
            names.append(key)
            obj.data.materials.append(mats["crescent_" + key])
        poly.material_index = names.index(key)
    return k.smooth(obj, 60)


def materials():
    pal = k.level_palette()
    return {
        "backing": k.material("arrow_backing", palette=0x52, metallic=0.2, roughness=0.6),
        "gem": k.material("arrow_gem", palette=0x5b, metallic=0.3, roughness=0.22),
        "gem_dark": k.material("arrow_gem_dark", palette=0x55, metallic=0.3, roughness=0.22),
        "gem_under": k.material("arrow_gem_under", palette=0x53, metallic=0.3, roughness=0.3),
        "crescent_deep": k.material("arrow_crescent_deep", palette=0xf2, roughness=0.35, emission=pal[0xf3],
                                    emission_strength=0.35),
        "crescent_dark": k.material("arrow_crescent_dark", palette=0xf4, roughness=0.35, emission=pal[0xf5],
                                    emission_strength=0.5),
        "crescent_red": k.material("arrow_crescent_red", palette=0xf6, roughness=0.3, emission=pal[0xf6],
                                   emission_strength=0.75),
        "crescent_warm": k.material("arrow_crescent_warm", palette=0xf8, roughness=0.3, emission=pal[0xf9],
                                    emission_strength=1.2),
        "crescent_hot": k.material("arrow_crescent_hot", palette=0xfb, roughness=0.25, emission=pal[0xfb],
                                   emission_strength=1.5),
    }


def build_arrow(mats):
    backing(mats)
    gem(mats)
    crescent(mats)
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
    build_arrow(materials())
    used = {m.name for o in bpy.context.scene.objects if o.type == "MESH" for m in o.data.materials}
    print("== arrow_purple (5 1): %d triangles, %d materials" % (triangles(), len(used)))
    if "check" in options:
        sheet = options["check"]
        k.check_silhouette(os.path.join(sheet, "enemy_5.png") if os.path.isdir(sheet) else sheet, 1)
    bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
    path = os.path.join(outdir, "arrow_purple.glb")
    k.export(path)
    print("%s: %d bytes" % (path, os.path.getsize(path)))
    if "preview" in options:
        k.preview(options["preview"] + "arrow_purple")


if __name__ == "__main__":
    build()
