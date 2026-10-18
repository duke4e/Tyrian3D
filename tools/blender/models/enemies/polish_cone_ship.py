"""The silver arrowhead with the glowing nose (sheet M, sprite 89: 2x2, 24 x 28; its frames 89, 91
and 93 only brighten the light; models.cfg: sprite m 89 cone_ship yaw=0).

Polish (2026-10-18), after the 4x upscale: a dark red nose cone with a glowing core, two big
curved silver blades that sweep out from behind it to shoulders at the sides and curve back in to
two prongs at the bottom, and between them a dark spine with two small grey-green lights. Each
blade is one lofted piece, highest at its inner edge (the bright line along the slot) and falling
away to its rounded outer edge; its leading edge is raised into a rim.

The sprite is symmetric about its column 12: the model is built about x = 0 and moved there
(AXIS_X).
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
import bpy  # noqa: E402
import tyrkit as k  # noqa: E402
from mathutils import Matrix, Vector  # noqa: E402

AXIS_X = 0.5   # the sprite's axis of symmetry (the middle of its column 12), model x
BASE = 0.55    # the blades' rims
BOTTOM = 0.2


def row_y(row):
    """Blender y of the centre of sprite pixel row `row` (the sprite's top is +y)."""
    return 14 - (row + 0.5)


def lerp_table(table, y):
    """Linear interpolation in [(y, value), ...] sorted by y."""
    if y <= table[0][0]:
        return table[0][1]
    for (y0, v0), (y1, v1) in zip(table, table[1:]):
        if y <= y1:
            return v0 + (v1 - v0) * (y - y0) / (y1 - y0)
    return table[-1][1]


def quarter(d, r):
    """A quarter circle rising from 0 at d = 0 to 1 at d = r (rounds an edge of radius r)."""
    if d <= 0:
        return 0.0
    if d >= r:
        return 1.0
    return math.sqrt(1 - (1 - d / r) ** 2)


# --- The blades -------------------------------------------------------------------------------------
# The left blade (x < 0), from its bottom tip (row 26) to its top tip beside the nose (row 8).
# Outer edge: the sprite's silhouette with its dark outline (the model replaces both): the prong,
# the step at row 15 under the shoulder, the shoulder (rows 12-14), the leading edge sweeping in to
# the nose (rows 10-11) and the narrow tip rising beside it (rows 8-9).
OUTER = [(-12.6, -1.15), (-12.2, -2.4), (-11.0, -3.15), (-9.0, -4.2), (-7.0, -5.2), (-5.0, -5.85),
         (-3.0, -6.25), (-2.0, -6.45), (-1.45, -6.9), (-1.0, -7.85), (-0.6, -8.2), (0.6, -8.2), (1.4, -8.05),
         (2.0, -7.65), (2.6, -7.1), (3.2, -6.45), (3.7, -5.6), (4.1, -4.4), (4.4, -3.2), (4.8, -2.6),
         (5.5, -2.45), (6.0, -2.25), (6.3, -1.95)]
# Inner edge: along the slot, then stepping out round the nose's glowing core.
INNER = [(-12.6, -1.05), (-12.2, -0.72), (2.5, -0.72), (3.4, -1.45), (6.3, -1.55)]
# The height of the inner edge's ridge above BASE.
RIDGE = [(-12.6, 1.1), (-11.5, 1.7), (-8.0, 2.25), (-3.0, 2.75), (1.0, 3.15), (3.5, 3.15), (5.0, 3.0),
         (5.8, 2.6), (6.3, 1.8)]
# The height of the outer part above BASE.
RIM = [(-12.6, 0.2), (-3.0, 0.3), (-1.6, 0.4), (-0.8, 0.6), (1.5, 0.7), (4.0, 0.8), (6.3, 0.8)]
# A raised rim just inside the outer edge along the shoulder and the leading edge: the bright line
# the sprite draws from the nose out to the shoulder's corner (rows 10-14).
CREST = [(-1.3, 0.0), (-0.6, 0.75), (0.5, 0.95), (2.0, 1.1), (4.0, 1.0), (4.6, 0.5), (5.0, 0.0)]


def edge_curve(table, y0=-12.6, y1=6.3, step=0.02):
    """The edge given by table (x as a function of y) as points from the bottom tip to the top."""
    count = int(round((y1 - y0) / step))
    return [(lerp_table(table, y0 + (y1 - y0) * i / count), y0 + (y1 - y0) * i / count) for i in range(count + 1)]


def resample(points, ts):
    """The points at the fractions ts (0-1) of the polyline's length."""
    lengths = [0.0]
    for (ax, ay), (bx, by) in zip(points, points[1:]):
        lengths.append(lengths[-1] + math.hypot(bx - ax, by - ay))
    out, j = [], 0
    for t in ts:
        target = t * lengths[-1]
        while j < len(lengths) - 2 and lengths[j + 1] < target:
            j += 1
        f = (target - lengths[j]) / max(lengths[j + 1] - lengths[j], 1e-9)
        (ax, ay), (bx, by) = points[j], points[j + 1]
        out.append((ax + (bx - ax) * f, ay + (by - ay) * f))
    return out


INNER_STEPS = (0.0, 0.1, 0.25, 0.45, 0.7)  # distances from the inner edge (the bright strip)
OUTER_STEPS = (1.7, 1.2, 0.8, 0.45, 0.2, 0.07, 0.0)  # distances from the outer edge (rounding, crest)
MIDDLE = 6


def section_distances(length):
    """Where the points of a section lie, as distances from its inner edge: close together near
    both edges (a constant-width strip along the inner edge), evenly between."""
    a = min(1.0, length / 2.6)
    b = min(1.0, length / 4.2)
    inner = [d * a for d in INNER_STEPS]
    outer = [length - d * b for d in OUTER_STEPS]
    middle = [inner[-1] + (outer[0] - inner[-1]) * (i + 1) / (MIDDLE + 1) for i in range(MIDDLE)]
    return inner + middle + outer


def blade_rings(count=34, n_bottom=4):
    """The left blade's sections: each runs from a point of the inner edge to the point at the same
    fraction of the outer edge's length, so the sections fan round the shoulder and along the
    leading edge and cross every edge squarely. Over each section the top rises from the rounded
    outer edge (with the crest just inside it where there is one) to the ridge at the inner edge."""
    # More sections near the tips, where the blade narrows.
    ts = [0.012 + 0.976 * (i / (count - 1) - 0.06 * math.sin(2 * math.pi * i / (count - 1))) for i in range(count)]
    inner = resample(edge_curve(INNER), ts)
    outer = resample(edge_curve(OUTER), ts)
    rings = []
    for (xi, yi), (xo, yo) in zip(inner, outer):
        length = max(math.hypot(xi - xo, yi - yo), 0.05)
        ridge, rim = lerp_table(RIDGE, yi), lerp_table(RIM, (yi + yo) / 2)
        crest = lerp_table(CREST, yo)
        points = []
        for d_in in section_distances(length):  # over the top, from the inner edge to the outer one
            s = 1 - d_in / length  # 1 at the inner edge, 0 at the outer
            x, y = xo + (xi - xo) * s, yo + (yi - yo) * s
            d_out = length - d_in
            height = rim + (ridge - rim) * math.sin(math.pi / 2 * s) ** 0.8  # convex, highest at the inner edge
            height += crest * math.exp(-((d_out - 0.75) / 0.6) ** 2)
            rounding = min(quarter(d_out, min(0.75, length * 0.4)), quarter(d_in, min(0.4, length * 0.3)))
            points.append(Vector((x, y, BASE + height * rounding)))
        for i in range(1, n_bottom):  # back underneath
            t = i / n_bottom
            f = (1 - math.cos(math.pi * t)) / 2
            points.append(Vector((xo + (xi - xo) * f, yo + (yi - yo) * f, BASE - (BASE - BOTTOM) * math.sin(math.pi * t))))
        rings.append(points)
    return rings


def blade(mat, edge_mat):
    """Both blades: the left one lofted, the right one its mirror. The strip along the rounded
    inner edge and the crest along the leading edge take the brighter edge material (the sprite's
    white lines along the slot and from the nose out to the shoulders)."""
    rings = blade_rings()
    n = len(rings[0])
    tip_bottom = (-1.12, -12.68, BASE)
    tip_top = (-1.75, 6.38, BASE + 0.9)
    left = k.loft("blade_left", rings, mat, start_point=tip_bottom, end_point=tip_top)
    left.data.materials.append(edge_mat)
    sides = (len(rings) - 1) * n  # the loft's faces between rings come first, ring by ring
    crest_columns = (len(INNER_STEPS) + MIDDLE + 1, len(INNER_STEPS) + MIDDLE + 2)  # d_out 1.2-0.45
    for poly in left.data.polygons[:sides]:
        ring, column = divmod(poly.index, n)
        inner = column < len(INNER_STEPS) - 1 and poly.normal.z > 0.5 and 2 <= ring <= len(rings) - 4
        crest = column in crest_columns and lerp_table(CREST, poly.center.y) > 0.5
        if inner or crest:
            poly.material_index = 1
    k.smooth(left, 50)
    right = k.mirror_x(left, "blade_right")
    right.data.name = "blade_right"
    k.smooth(right, 50)


# --- The nose and the spine -------------------------------------------------------------------------

def nose(red, core, hot):
    """The dark red cone at the front (rows 5-10), with a glowing core along its top that is
    hottest at the bottom, where it meets the spine."""
    # Broad at rows 7-9 and quickly narrowing to the tip in rows 5-6, like an arch.
    profile = [(2.6, 2.4), (3.6, 3.3), (4.5, 3.65), (5.5, 3.45), (6.4, 3.05), (7.1, 2.35), (7.7, 1.6),
               (8.3, 0.95), (8.8, 0.45), (9.15, 0.0)]
    # Rounded on top, its underside flattened to stay above the ground.
    rings = [k.ring(y, r, r * 0.72, 18, z=1.0, bottom=0.3) for y, r in k.profile(profile, step=0.45) if r > 0]
    cone = k.loft("nose", rings, red, start_point=(0, 2.45, 1.0), end_point=(0, 9.15, 1.0))
    k.smooth(cone, 60)
    k.smooth(k.ellipsoid("core", (0, 5.0, 3.05), (1.25, 2.0, 0.7), core, 14, 8), 60)
    k.smooth(k.ellipsoid("core_hot", (0, 4.4, 3.3), (0.72, 1.2, 0.5), hot, 10, 6), 60)


def spine(dark, bezel, light):
    """The dark spine in the slot between the blades (rows 11-16), lower than their inner edges,
    with two small lights (rows 12 and 14)."""
    rings = []
    for y in [-2.75 + 6.6 * i / 13 for i in range(14)]:
        f = quarter(y + 2.8, 0.6)
        rings.append(k.ring(y, 0.95, 0.75 * f + 0.05, 12, z=1.45, bottom=1.4, power=2.5))
    k.smooth(k.loft("spine", rings, dark), 50)
    for row in (12, 14):
        y = row_y(row)
        k.smooth(k.ellipsoid(f"bezel{row}", (0, y, 2.15), (0.95, 0.75, 0.32), bezel, 12, 6), 60)
        k.smooth(k.ellipsoid(f"light{row}", (0, y, 2.4), (0.5, 0.45, 0.28), light, 10, 5), 60)


def tri_count():
    depsgraph = bpy.context.evaluated_depsgraph_get()
    total = 0
    for obj in bpy.context.scene.objects:
        if obj.type == "MESH":
            mesh = obj.evaluated_get(depsgraph).to_mesh()
            mesh.calc_loop_triangles()
            total += len(mesh.loop_triangles)
            obj.evaluated_get(depsgraph).to_mesh_clear()
    return total


def build():
    k.reset()

    silver = k.material("cone_silver", palette=10, metallic=0.55, roughness=0.24)
    edge = k.material("cone_edge", palette=13, metallic=0.55, roughness=0.18)
    red = k.material("cone_red", palette=116, metallic=0.3, roughness=0.22)
    core = k.material("cone_core", palette=122, roughness=0.3, emission=(255, 130, 20), emission_strength=2.6)
    hot = k.material("cone_hot", palette=126, roughness=0.3, emission=(255, 235, 150), emission_strength=3.2)
    dark = k.material("cone_spine", palette=3, metallic=0.45, roughness=0.35)
    bezel = k.material("cone_bezel", palette=7, metallic=0.5, roughness=0.3)
    light = k.material("cone_light", palette=12, roughness=0.2, emission=(165, 215, 165), emission_strength=0.8)

    blade(silver, edge)
    nose(red, core, hot)
    spine(dark, bezel, light)

    for obj in bpy.context.scene.objects:
        if obj.type == "MESH":
            obj.data.transform(Matrix.Translation((AXIS_X, 0, 0)))
    print("triangles:", tri_count())

    here = os.path.dirname(os.path.abspath(__file__))
    k.finish(os.path.join(here, "..", "..", "..", "..", "assets", "models", "enemies", "cone_ship.glb"))


build()
