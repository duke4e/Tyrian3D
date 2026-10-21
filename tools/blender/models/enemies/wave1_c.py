"""Enemies of wave 1, batch C, facing the way their sprites do (models.cfg: yaw=0 unless noted; the claw gate
is polish_claw_gate.py):

- purple_pod (sheet 5 47): a purple pod with a red strap and a golden clasp (HARVEST, LAVA RUN).
(The teal spiked mine, A 167, is polish_spike_mine.py's chrome mine in the sprite's colours: models.cfg color=sprite.)
(The crimson orb, K 195: polish_orb_crimson.py; DELI's gun arms, T 39 and 49: polish_deli_boss.py.)
- savara_fin_left / savara_fin_right (sheet F 153 / 163): the outer glowing fins of SAVARA's boss
  (their lower ends continue into the boss's next sprites).

Most parts are reliefs: solids over the outline of a part of the sprite (drawn below as letters),
their tops rounded off towards the outline, so the top view keeps the sprite's silhouette.

Run: Blender -b --factory-startup -P wave1_c.py -- [--only name,name] [--preview <dir>]
     [--sheets <TYR3D_EXTRACT sheets dir>] [--stats 1]
     (--sheets prints each model's silhouette overlap with its sprite, --stats the faces per part)
"""
import math
import os
import sys

import bpy
from mathutils import Vector, geometry

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
import tyrkit as k  # noqa: E402
import silhouette as s  # noqa: E402

OUT = os.path.join(HERE, "..", "..", "..", "..", "assets", "models", "enemies")


# --- Helpers ---------------------------------------------------------------------------------------

def px(col):
    """A 2x2 sprite's pixel column (its centre) as x."""
    return col + 0.5 - 12


def py(row):
    """A 2x2 sprite's pixel row (its centre) as y."""
    return 14 - (row + 0.5)


def art(text):
    """A 2x2 sprite's rows (24 x 28) from text whose rows start at the sprite's top."""
    rows = [line.ljust(24, ".") for line in text.strip("\n").split("\n")]
    return rows + ["." * 24] * (28 - len(rows))


def part(rows, chars):
    """The rows of an art with only the pixels whose letter is in chars covered."""
    return ["".join("#" if ch in chars else "." for ch in row) for row in rows]


def outline(rows, chars=None, epsilon=0.6):
    """The outline of the pixels of a part (letters in chars; all covered pixels if None)."""
    return s.outline(part(rows, chars) if chars else rows, 24, epsilon)


def round_edge(d, low, high, width):
    """Height across a rounded edge: low at the outline, rising as a quarter circle to high at width."""
    t = max(0.0, min(1.0, d / width))
    return low + (high - low) * math.sqrt(1 - (1 - t) ** 2)


def _densify(polygon, step):
    out = []
    n = len(polygon)
    for i in range(n):
        (ax, ay), (bx, by) = polygon[i], polygon[(i + 1) % n]
        count = max(1, int(math.ceil(math.hypot(bx - ax, by - ay) / step)))
        for j in range(count):
            t = j / count
            out.append((ax + (bx - ax) * t, ay + (by - ay) * t))
    return out


def _inside(x, y, polygon):
    inside = False
    n = len(polygon)
    for i in range(n):
        (ax, ay), (bx, by) = polygon[i], polygon[(i + 1) % n]
        if (ay > y) != (by > y) and x < ax + (y - ay) * (bx - ax) / (by - ay):
            inside = not inside
    return inside


def _seg_dist(x, y, a, b):
    (ax, ay), (bx, by) = a, b
    dx, dy = bx - ax, by - ay
    length2 = dx * dx + dy * dy
    t = 0.0 if length2 == 0 else max(0.0, min(1.0, ((x - ax) * dx + (y - ay) * dy) / length2))
    return math.hypot(x - ax - t * dx, y - ay - t * dy)


def relief(name, polygon, top, mats, bottom=0.0, spacing=0.55, cut=None, mat_fn=None, side_mat=0, smooth=50,
           band=2.5, coarse=3, lines=()):
    """A solid over a polygon (counter-clockwise [(x, y)], e.g. a sprite part's outline): its top at
    top(x, y, d), d the distance to the outline, its bottom at `bottom` (a height or a function
    bottom(x, y, d)), straight sides between. Outline edges where cut(a, b) is true are left out of
    d: the model goes on there into the next sprite. mats: a material or a list; mat_fn(x, y, z, d)
    picks a top face's material index (side_mat the sides'). The top is sampled every `spacing`
    within `band` of the outline (where edges round off), every `coarse` spacings further in; lines
    (polylines inside) become edges of the mesh, for crisp material borders and creases."""
    mats = mats if isinstance(mats, (list, tuple)) else [mats]
    boundary = _densify(polygon, spacing)
    n = len(boundary)
    segments = [(polygon[i], polygon[(i + 1) % len(polygon)]) for i in range(len(polygon))]
    measured = [sg for sg in segments if not (cut and cut(*sg))] or segments

    def dist(x, y):
        return min(_seg_dist(x, y, a, b) for a, b in measured)

    points = list(boundary)
    xs = [p[0] for p in polygon]
    ys = [p[1] for p in polygon]
    i0, j0 = math.floor(min(xs) / spacing), math.floor(min(ys) / spacing)
    for i in range(i0, math.ceil(max(xs) / spacing) + 1):
        for j in range(j0, math.ceil(max(ys) / spacing) + 1):
            gx, gy = i * spacing, j * spacing
            if not _inside(gx, gy, polygon):
                continue
            edge = min(_seg_dist(gx, gy, a, b) for a, b in segments)
            if edge <= spacing * 0.35:
                continue
            if dist(gx, gy) > band and (i % coarse or j % coarse):
                continue
            if any(_seg_dist(gx, gy, a, b) < spacing * 0.5 for line in lines for a, b in zip(line, line[1:])):
                continue
            points.append((gx, gy))
    constraints = []
    for line in lines:
        dense = []
        for a, b in zip(line, line[1:]):
            count = max(1, int(math.ceil(math.hypot(b[0] - a[0], b[1] - a[1]) / spacing)))
            dense += [(a[0] + (b[0] - a[0]) * j / count, a[1] + (b[1] - a[1]) * j / count) for j in range(count)]
        dense.append(line[-1])
        inside = [p for p in dense if _inside(p[0], p[1], polygon) and
                  min(_seg_dist(p[0], p[1], a, b) for a, b in segments) > spacing * 0.35]
        first = len(points)
        points += inside
        constraints += [(first + j, first + j + 1) for j in range(len(inside) - 1)
                        if math.dist(inside[j], inside[j + 1]) < spacing * 1.5]
    result = geometry.delaunay_2d_cdt([Vector(p) for p in points], constraints, [list(range(n))], 1, 1e-6)
    coords, faces, origins = result[0], result[2], result[3]
    m = len(coords)
    heights = [top(c.x, c.y, dist(c.x, c.y)) for c in coords]
    vertices = [(c.x, c.y, h) for c, h in zip(coords, heights)]
    out_faces, face_mats = [], []
    for f in faces:
        out_faces.append(tuple(f))
        if mat_fn is not None:
            cx = sum(coords[i].x for i in f) / len(f)
            cy = sum(coords[i].y for i in f) / len(f)
            cz = sum(heights[i] for i in f) / len(f)
            face_mats.append(mat_fn(cx, cy, cz, dist(cx, cy)))
        else:
            face_mats.append(0)
    index = {}
    for i, orig in enumerate(origins):
        for o in orig:
            index[o] = i
    if callable(bottom):
        # A shaped bottom: the top's triangles again, facing down.
        vertices += [(c.x, c.y, bottom(c.x, c.y, dist(c.x, c.y))) for c in coords]
        out_faces += [tuple(m + i for i in reversed(f)) for f in faces]
        face_mats += [side_mat] * len(faces)
        low = [m + index[j] for j in range(n)]
    else:
        # A flat bottom: the outline alone, triangulated.
        flat = geometry.delaunay_2d_cdt([Vector(p) for p in boundary], [], [list(range(n))], 1, 1e-6)
        start = len(vertices)
        vertices += [(c.x, c.y, bottom) for c in flat[0]]
        out_faces += [tuple(start + i for i in reversed(f)) for f in flat[2]]
        face_mats += [side_mat] * len(flat[2])
        low_index = {}
        for i, orig in enumerate(flat[3]):
            for o in orig:
                low_index[o] = start + i
        low = [low_index[j] for j in range(n)]
    # The sides, along the boundary (the first n input points, in order).
    for j in range(n):
        a, b = index[j], index[(j + 1) % n]
        out_faces.append((a, low[j], low[(j + 1) % n], b))
        face_mats.append(side_mat)
    obj = k.mesh_object(name, vertices, out_faces)
    for mat in mats:
        obj.data.materials.append(mat)
    for poly, mi in zip(obj.data.polygons, face_mats):
        poly.material_index = mi
    k.recalc_normals(obj)
    return k.smooth(obj, smooth)


# --- Round ones ------------------------------------------------------------------------------------

def ellipsoid_part(name, centre, radii, mat, y0, y1, segments=40, rings_count=14):
    """The part of an ellipsoid between y0 and y1 (absolute), closed at the cut."""
    cx, cy, cz = centre
    rx, ry, rz = radii
    rings = []
    for i in range(rings_count + 1):
        y = y0 + (y1 - y0) * i / rings_count
        f = max(0.0, 1 - ((y - cy) / ry) ** 2) ** 0.5
        if f > 1e-3:
            rings.append(k.ring(y, rx * f, rz * f, segments, z=cz, x=cx))
    return k.smooth(k.loft(name, rings, mat, start_point=(cx, y0, cz), end_point=(cx, y1, cz)), 70)


def purple_pod():
    k.reset()
    shell = k.material("pod_shell", palette=87, metallic=0.3, roughness=0.28)
    lower = k.material("pod_lower", palette=85, metallic=0.3, roughness=0.3)
    strap = k.material("pod_strap", palette=243, metallic=0.25, roughness=0.35)
    edge = k.material("pod_edge", palette=82, metallic=0.3, roughness=0.4)
    gold = k.material("pod_gold", palette=250, metallic=0.85, roughness=0.22)
    c = (0.0, 0.5, 0.0)
    radii = (12.0, 13.5, 9.0)
    ellipsoid_part("upper", c, radii, shell, 0.0, c[1] + radii[1])
    ellipsoid_part("lower", c, radii, lower, c[1] - radii[1], 0.0)

    def half_width(y):
        return radii[0] * max(0.0, 1 - ((y - c[1]) / radii[1]) ** 2) ** 0.5

    squash = radii[2] / radii[0]
    profile = [(-2.6, half_width(-2.6) - 0.1), (-2.3, half_width(-2.3) + 0.5), (2.3, half_width(2.3) + 0.5),
               (2.6, half_width(2.6) - 0.1)]
    k.smooth(k.lathe("strap", profile, strap, segments=64, squash=squash), 50)
    for y in (-2.9, 2.9):
        k.smooth(k.lathe(f"edge{y}", [(y - 0.35, half_width(y) - 0.1), (y, half_width(y) + 0.3),
                                      (y + 0.35, half_width(y) - 0.1)], edge, segments=64, squash=squash), 60)
    # The golden clasp on top (and its twin underneath).
    for z, name in ((radii[2] + 0.35, "clasp"), (-radii[2] - 0.35, "clasp_under")):
        clasp = k.box(name, (0.0, 0.0, z), (2.4, 6.4, 1.2), gold)
        k.bevel(clasp, 0.4, 2)
    k.smooth(k.ellipsoid("stud", (0.0, 0.0, radii[2] + 1.0), (0.8, 1.2, 0.5), gold, 12, 6), 60)


# --- SAVARA's boss fins (sheet F 153 and 163) ------------------------------------------------------
# f the fin (its lower end goes on into the boss's next sprite), x bits of the boss's hull.

FIN_LEFT = art("""
........................
........................
........................
........................
........................
........................
........................
........................
........................
........................
........................
..............fffffffff.
..............fffffffff.
..............fffffffff.
..............fffffffff.
..............fffffffff.
..............fffffffff.
..............fffffffff.
..............fffffffff.
..............fffffffffx
..............fffffffffx
..............fffffffffx
..............fffffffffx
..............fffffffffx
..............fffffffffx
.............xfffffffffx
............xxfffffffffx
...........xxxfffffffffx
""")

FIN_RIGHT = art("""
........................
........................
........................
........................
........................
........................
........................
........................
........................
........................
........................
........................
..fffffffff.............
..fffffffff.............
..fffffffff.............
..fffffffff.............
..fffffffff.............
..fffffffff.............
..fffffffff.............
x.fffffffff.............
xxfffffffff.............
xxfffffffff.............
xxfffffffff.............
xxfffffffff.............
xxfffffffff.............
xxfffffffff.............
xxfffffffffx............
xxfffffffffxx...........
""")


def savara_fin(rows, dx, dy):
    """dx, dy: where the fin lies relative to F 153's (the fins are the same)."""
    k.reset()
    frame = k.material("fin_frame", palette=66, metallic=0.55, roughness=0.35)
    hull = k.material("fin_hull", palette=69, metallic=0.4, roughness=0.4)
    panel = k.material("fin_panel", palette=117, roughness=0.3, emission=(230, 40, 0), emission_strength=1.0)
    deep = k.material("fin_deep", palette=115, roughness=0.3, emission=(170, 10, 0), emission_strength=0.8)
    glyph = k.material("fin_glyph", palette=121, roughness=0.25, emission=(255, 120, 20), emission_strength=2.0)
    groove = k.material("fin_groove", palette=113, roughness=0.4)
    bottom = lambda a, b: a[1] < -13.99 and b[1] < -13.99  # noqa: E731
    relief("fin", outline(rows, "f"), lambda x, y, d: round_edge(d, 4.0, 6.6, 0.8), frame, cut=bottom)
    hull_cut = lambda a, b: bottom(a, b) or (abs(a[0]) > 11.99 and abs(b[0]) > 11.99)  # noqa: E731
    for i, piece in enumerate(_islands(part(rows, "x"))):
        relief(f"hull{i}", s.outline(piece, 24, 0.6), lambda x, y, d: round_edge(d, 1.2, 2.8, 0.8), hull,
               cut=hull_cut)

    def at(x, y):
        return (x + dx, y + dy)

    # The glowing panel, inset in the frame, and its glyph (the sprite's bright lines).
    x0, x1, y0 = px(15) - 0.5, px(21) + 0.5, py(12) + 0.5
    relief("panel", [at(x0, -13.92), at(x1, -13.92), at(x1, y0), at(x0, y0)],
           lambda x, y, d: round_edge(d, 6.75, 7.3, 0.5), [panel, deep], bottom=6.0, spacing=0.5, band=0.8, cut=bottom,
           mat_fn=lambda x, y, z, d: 1 if y - dy > py(16.5) else 0)
    bars = [((15, 12.2), (15, 27.4)), ((20, 15.0), (20, 27.4)), ((15, 18), (20.6, 18)), ((15, 20), (18.4, 20)),
            ((15, 26), (21.0, 26))]
    for i, ((c0, r0), (c1, r1)) in enumerate(bars):
        a, b = at(px(c0), py(r0)), at(px(c1), py(r1))
        w = 0.8
        size = (w, abs(a[1] - b[1]), 0.6) if abs(a[0] - b[0]) < 1e-6 else (abs(b[0] - a[0]) + w, w, 0.6)
        bar = k.box(f"bar{i}", ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, 7.45), size, glyph)
        k.bevel(bar, 0.15, 1)
    a, b = at(px(17) - 0.4, py(17) - 0.2), at(px(17) + 0.4, py(12) + 0.2)
    k.box("groove", ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, 7.45), (b[0] - a[0], b[1] - a[1], 0.4), groove)


def _islands(rows):
    """The separate pieces of a mask (4-connected), each as rows of its own."""
    seen = set()
    pieces = []
    for r, row in enumerate(rows):
        for c, ch in enumerate(row):
            if ch == "#" and (r, c) not in seen:
                stack, cells = [(r, c)], set()
                seen.add((r, c))
                while stack:
                    cr, cc = stack.pop()
                    cells.add((cr, cc))
                    for nr, nc in ((cr + 1, cc), (cr - 1, cc), (cr, cc + 1), (cr, cc - 1)):
                        if 0 <= nr < len(rows) and 0 <= nc < 24 and rows[nr][nc] == "#" and (nr, nc) not in seen:
                            seen.add((nr, nc))
                            stack.append((nr, nc))
                pieces.append(["".join("#" if (rr, cc) in cells else "." for cc in range(24))
                               for rr in range(len(rows))])
    return pieces


def savara_fin_left():
    savara_fin(FIN_LEFT, 0.0, 0.0)


def savara_fin_right():
    savara_fin(FIN_RIGHT, -12.0, -1.0)


# --- Running ---------------------------------------------------------------------------------------

# name: (builder, sheet, sprite used for the silhouette check)
MODELS = {
    "purple_pod": (purple_pod, "5", 47),
    "savara_fin_left": (savara_fin_left, "F", 153),
    "savara_fin_right": (savara_fin_right, "F", 163),
}


def main():
    options = k.args()
    only = options.get("only", "").split(",") if "only" in options else None
    for name, (build, sheet, sprite) in MODELS.items():
        if only and name not in only:
            continue
        build()
        if "stats" in options:
            for obj in bpy.context.scene.objects:
                if obj.type == "MESH":
                    mesh = obj.evaluated_get(bpy.context.evaluated_depsgraph_get()).to_mesh()
                    print("  ", name, obj.name, len(mesh.polygons), "faces")
        if "sheets" in options:
            print("model", name)
            k.check_silhouette(os.path.join(options["sheets"], f"enemy_{sheet.upper()}.png"), sprite)
        k.export(os.path.join(OUT, name + ".glb"))
        if "preview" in options:
            bpy.context.scene.view_settings.view_transform = "Standard"
            k.preview(os.path.join(options["preview"], name))


main()
