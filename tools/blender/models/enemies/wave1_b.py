"""Enemies of wave 1, batch B, modelled as their sprites look (models.cfg: yaw=0):

(tank_pod_left / tank_pod_right, C 197 / C 199, are built by polish_tank_pod.py; arm_ball_left /
arm_ball_right, V 89 / V 93, by polish_arm_bridge.py; flame_drop, 3 267, by polish_flame_drop.py; comet_tail /
comet_head, 5 203 / 5 241, by polish_comet.py.)
- fire_orb (sheet A 277): a glossy glowing orange orb, red round the side; the sprite pulses darker
  (glow option).
- cell_sphere (sheet 3 229 lava, 5 89 ice): a sphere of round cells with ridges between them, one
  grey model in palette shades taking each sprite's colour (color=sprite).
- rod_top, rod_tail (sheet 5 55, 5 93): the upper and lower half of ?TUNNEL?'s mechanical rod
  lying on the ground: a knob, flanges, a cowl with red lights, a pointed tail.

usage: Blender -b --factory-startup -P wave1_b.py -- [--only name,name] [--preview <prefix>]
       [--sheets <TYR3D_EXTRACT sheets dir>]   (--sheets: print each model's silhouette overlap)
"""
import math
import os
import random
import sys

import bmesh
import bpy
from mathutils import Vector

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
import tyrkit as k  # noqa: E402

W, H = 24, 28  # a 2x2 sprite


# --- Helpers -------------------------------------------------------------------------------------

def px(col):
    """The x of a pixel column's centre."""
    return col + 0.5 - W / 2


def py(row):
    """The y of a pixel row's centre."""
    return H / 2 - (row + 0.5)


def edges(points):
    """(column, row) pixel-edge coordinates to model (x, y), counter-clockwise."""
    return ccw([(c - W / 2, H / 2 - r) for c, r in points])


def ccw(outline):
    area = sum(outline[i][0] * outline[(i + 1) % len(outline)][1] - outline[(i + 1) % len(outline)][0] * outline[i][1]
               for i in range(len(outline)))
    return outline if area > 0 else outline[::-1]


def rows(text):
    return [line.ljust(W, ".") for line in text.strip("\n").split("\n")]


def pal(name, index, metallic=0.3, roughness=0.4, glow=None, color=None):
    """A palette material; glow: emission strength, in the palette colour (or color)."""
    if glow:
        return k.material(name, palette=index, metallic=metallic, roughness=roughness,
                          emission=color or k.level_palette()[index], emission_strength=glow)
    return k.material(name, palette=index, metallic=metallic, roughness=roughness)


def round_part(name, profile, mat, axis="y", at=0.0, z=0.0, squash=1.0, segments=24, floor=None, power=2.0,
               cap=True):
    """A round part along an axis (y: up the screen, x: right): profile [(t, radius)] in increasing t,
    centred at `at` (x for axis y, y for axis x) and height z; cross-sections squashed in height by
    `squash` (power > 2: boxier); points below `floor` are flattened onto it (parts on the ground)."""
    rings = []
    for t, r in profile:
        r = max(r, 0.03)
        ring = []
        for i in range(segments):
            a = 2 * math.pi * i / segments
            c, s = math.cos(a), math.sin(a)
            u = math.copysign(abs(c) ** (2 / power), c) * r
            v = z + math.copysign(abs(s) ** (2 / power), s) * r * squash
            if floor is not None:
                v = max(v, floor)
            ring.append(Vector((at + u, t, v)) if axis == "y" else Vector((t, at - u, v)))
        rings.append(ring)
    first, last = profile[0][0], profile[-1][0]
    zc = z if floor is None else max(z, floor)
    start = (at, first, zc) if axis == "y" else (first, at, zc)
    end = (at, last, zc) if axis == "y" else (last, at, zc)
    obj = k.loft(name, rings, mat, cap_start=cap, cap_end=cap, start_point=start, end_point=end)
    return k.smooth(obj, 50)


def _inside(polygon, x, y):
    inside = False
    for i in range(len(polygon)):
        (ax, ay), (bx, by) = polygon[i], polygon[(i + 1) % len(polygon)]
        if (ay > y) != (by > y) and x < ax + (y - ay) * (bx - ax) / (by - ay):
            inside = not inside
    return inside


def _edge_distance(polygon, x, y):
    best = 1e9
    for i in range(len(polygon)):
        (ax, ay), (bx, by) = polygon[i], polygon[(i + 1) % len(polygon)]
        dx, dy = bx - ax, by - ay
        t = max(0.0, min(1.0, ((x - ax) * dx + (y - ay) * dy) / (dx * dx + dy * dy or 1e-9)))
        best = min(best, math.hypot(x - ax - t * dx, y - ay - t * dy))
    return best


def cushion(name, outline, z0, top, mat, rounding=1.5, spacing=0.7, smooth_angle=50, values=None):
    """A part in the outline [(x, y)] (counter-clockwise) standing on z0: its top follows top(x, y)
    and its edge rounds over in a quarter circle of `rounding` pixels into straight sides. The top
    is a triangulation of points every `spacing` pixels (denser along the edge), so it can bend.
    values: if a list, gets top(x, y)-based values per vertex for band_split (None for the base)."""
    outline = ccw(list(outline))
    boundary = []  # the outline every half spacing
    for i in range(len(outline)):
        a, b = Vector(outline[i]), Vector(outline[(i + 1) % len(outline)])
        steps = max(1, int(math.ceil((b - a).length / (spacing * 0.5))))
        boundary += [a.lerp(b, s / steps) for s in range(steps)]
    points = [Vector((p.x, p.y)) for p in boundary]
    # Rings along the edge for the rounding, where they keep their distance from the outline.
    for p_index, p in enumerate(boundary):
        a, b = boundary[p_index - 1], boundary[(p_index + 1) % len(boundary)]
        tangent = (b - a).normalized()
        inward = Vector((-tangent.y, tangent.x))
        for f in (0.08, 0.3, 0.6, 1.0):
            q = p + inward * rounding * f
            if _inside(outline, q.x, q.y) and abs(_edge_distance(outline, q.x, q.y) - rounding * f) < 0.1 * rounding:
                points.append(q)
    xs, ys = [p[0] for p in outline], [p[1] for p in outline]
    y = min(ys) + spacing / 2
    while y < max(ys):
        x = min(xs) + spacing / 2 + (spacing / 2 if int((y - min(ys)) / spacing) % 2 else 0)
        while x < max(xs):
            if _inside(outline, x, y) and _edge_distance(outline, x, y) > rounding * 1.15:
                points.append(Vector((x, y)))
            x += spacing
        y += spacing * 0.87
    coords, _, faces, orig, _, _ = mathutils_geometry().delaunay_2d_cdt(points, [], [list(range(len(boundary)))], 1,
                                                                          1e-4)
    out_of = {}
    for o, origins in enumerate(orig):
        for i in origins:
            out_of[i] = o
    verts = []
    for c in coords:
        d = _edge_distance(outline, c.x, c.y)
        z_top = top(c.x, c.y)
        r = min(rounding, max(z_top - z0, 0.01))
        z = z_top - r + math.sqrt(max(0.0, r * r - (r - min(d, r)) ** 2))
        verts.append(Vector((c.x, c.y, max(z, z0))))
    n = len(verts)
    faces = [list(f) for f in faces]
    ring = [out_of[i] for i in range(len(boundary))]
    verts += [Vector((verts[o].x, verts[o].y, z0)) for o in ring]
    for i in range(len(ring)):
        j = (i + 1) % len(ring)
        faces.append([n + i, n + j, ring[j], ring[i]])
    faces.append([n + i for i in reversed(range(len(ring)))])
    if values is not None:
        values += [top(v.x, v.y) for v in verts[:n]] + [None] * len(ring)
    obj = k.mesh_object(name, verts, faces, mat)
    k.recalc_normals(obj)
    return k.smooth(obj, smooth_angle)


def mathutils_geometry():
    import mathutils.geometry
    return mathutils.geometry


def band_split(obj, values, bands, face_band=None, smooth_angle=60):
    """Colours a mesh in bands of a value per vertex, cutting its faces along the bands' borders so
    the borders are smooth lines rather than the faces' zigzag. bands: [(lowest value, material)],
    ascending (the first takes everything below the second). face_band(polygon) may give a band for
    a whole face (or None); vertices whose value is None go to the first band."""
    mesh = obj.data
    co = [v.co.copy() for v in mesh.vertices]
    vals = [bands[0][0] - 1 if v is None else v for v in values]
    thresholds = [b[0] for b in bands]
    cuts = {}

    def cut(a, b, t):
        key = (min(a, b), max(a, b), t)
        if key not in cuts:
            f = (t - vals[a]) / (vals[b] - vals[a])
            co.append(co[a].lerp(co[b], f))
            vals.append(t)
            cuts[key] = len(co) - 1
        return cuts[key]

    def clip(poly, t, above):
        out = []
        for i in range(len(poly)):
            a, b = poly[i], poly[(i + 1) % len(poly)]
            ina = (vals[a] >= t) == above
            inb = (vals[b] >= t) == above
            if ina:
                out.append(a)
            if ina != inb:
                out.append(cut(a, b, t))
        return out

    faces, materials = [], []
    for poly in mesh.polygons:
        indices = list(poly.vertices)
        forced = face_band(poly) if face_band else None
        if forced is not None:
            faces.append(indices)
            materials.append(forced)
            continue
        low, high = min(vals[i] for i in indices), max(vals[i] for i in indices)
        for b in range(len(bands)):
            lo = thresholds[b] if b > 0 else -1e9
            hi = thresholds[b + 1] if b + 1 < len(bands) else 1e9
            if high < lo or low >= hi:
                continue
            piece = indices
            if b > 0 and low < lo:
                piece = clip(piece, lo, True)
            if b + 1 < len(bands) and high >= hi:
                piece = clip(piece, hi, False)
            if len(piece) >= 3:
                faces.append(piece)
                materials.append(b)
    new = bpy.data.meshes.new(mesh.name)
    new.from_pydata([tuple(c) for c in co], [], faces)
    for _, mat in bands:
        new.materials.append(mat)
    for poly, m in zip(new.polygons, materials):
        poly.material_index = m
    new.validate()
    obj.data = new
    bm = bmesh.new()
    bm.from_mesh(new)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-4)
    bmesh.ops.dissolve_degenerate(bm, edges=bm.edges, dist=1e-4)
    bm.to_mesh(new)
    bm.free()
    k.recalc_normals(obj)
    return k.smooth(obj, smooth_angle)


def smoothstep(a, b, x):
    t = min(1.0, max(0.0, (x - a) / (b - a)))
    return t * t * (3 - 2 * t)


# --- A 277: the glowing orb ----------------------------------------------------------------------

def fire_orb():
    """A glossy orange orb, red round the side; the game's light gives it the sprite's highlight."""
    shades = [(-9.0, 119), (0.22, 120), (0.38, 121), (0.52, 122)]  # by height on the orb
    bands = [(lowest, pal(f"orb_{index}", index, metallic=0.0, roughness=0.12, glow=0.3)) for lowest, index in shades]
    centre, radii = Vector((0.0, 0.5, 8.4)), Vector((8.9, 8.5, 8.2))
    orb = k.smooth(k.ellipsoid("orb", centre, radii, bands[-1][1], 64, 32), 80)
    band_split(orb, [(v.co.z - centre.z) / radii.z for v in orb.data.vertices], bands, smooth_angle=80)


# --- 3 229 / 5 89: the sphere of cells -----------------------------------------------------------

def cell_sphere():
    # Shades of the lava ramp (7); color=sprite gives each sprite's ramp (ice: 3).
    bands = [(0.0, pal("cells_floor", 0x71, metallic=0.1, roughness=0.6)),
             (0.1, pal("cells_low", 0x73, metallic=0.1, roughness=0.5)),
             (0.35, pal("cells_wall", 0x75, metallic=0.1, roughness=0.4)),
             (0.72, pal("cells_ridge", 0x77, metallic=0.1, roughness=0.35)),
             (0.86, pal("cells_vein", 0x79, metallic=0.1, roughness=0.3)),
             (0.95, pal("cells_crest", 0x7b, metallic=0.1, roughness=0.3))]
    centre, radius, squash = Vector((-0.5, 0.5, 9.4)), 11.4, 0.82
    rng = random.Random(229)
    seeds, count = [], 30
    for i in range(count):  # spread evenly (a Fibonacci sphere), then jittered
        zz = 1 - 2 * (i + 0.5) / count
        rr = math.sqrt(1 - zz * zz)
        a = i * math.pi * (3 - math.sqrt(5))
        v = Vector((rr * math.cos(a), rr * math.sin(a), zz)) + Vector([rng.uniform(-0.2, 0.2) for _ in range(3)])
        seeds.append(v.normalized())
    pit = [rng.uniform(0.62, 0.74) for _ in seeds]  # where each cell's pit begins (0 centre, 1 edge)
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=5, radius=1.0)
    values = []
    for v in bm.verts:
        n = v.co.normalized()
        d = sorted((n.angle(s), i) for i, s in enumerate(seeds))
        q = 2 * d[0][0] / (d[0][0] + d[1][0])  # 0 at the cell's middle, 1 on its edge
        start = pit[d[0][1]]
        h = 0.12 * q / start if q < start else 0.12 + 0.8 * smoothstep(start, start + 0.22, q)
        h = min(1.0, h + 0.08 * smoothstep(0.92, 1.0, q))
        r = radius * (1 - 0.15 * (1 - h))
        v.co = centre + Vector((n.x * r, n.y * r, n.z * r * squash))
        values.append(h)
    mesh = bpy.data.meshes.new("cells")
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new("cells", mesh)
    bpy.context.scene.collection.objects.link(obj)
    band_split(obj, values, bands, smooth_angle=80)


# --- 5 55 / 5 93: the rod on the ground ----------------------------------------------------------

ROD_AXIS_X, ROD_Z, ROD_SQUASH = -0.5, 3.4, 0.85


def rod_top():
    grey = pal("rod_grey", 6, metallic=0.6, roughness=0.35)
    light = pal("rod_light", 9, metallic=0.6, roughness=0.3)
    dark = pal("rod_dark", 3, metallic=0.5, roughness=0.5)
    red = pal("rod_red", 0x74, metallic=0.2, roughness=0.35, glow=0.25, color=(150, 10, 0))
    lamp = pal("rod_lamp", 0x7c, metallic=0.0, roughness=0.2, glow=1.5, color=(255, 120, 30))
    floor = 0.0
    # The spine from the bottom edge up to the knob.
    round_part("spine", [(-14.0, 3.3), (py(23), 2.6), (py(20), 2.9), (py(13), 3.0), (py(9), 3.0), (py(8), 3.0)],
               grey, at=ROD_AXIS_X, z=ROD_Z, squash=ROD_SQUASH, floor=floor, cap=True)
    # The knob on top (rows 0-4) and the flange under it (rows 5-8).
    round_part("knob", [(py(4.6), 2.8), (py(4), 3.5), (py(2), 3.6), (py(0.8), 2.8), (py(0.2), 1.5), (py(-0.1), 0.3)],
               light, at=-1.0, z=ROD_Z + 0.4, squash=ROD_SQUASH, floor=floor)
    round_part("flange", [(py(8.6), 4.6), (py(8.3), 5.2), (py(5.3), 5.6), (py(4.6), 4.8)], grey, at=ROD_AXIS_X,
               z=ROD_Z, squash=ROD_SQUASH, floor=floor, power=2.6)
    # The cowl over the shoulders (rows 13-20), open below where the red lights show.
    cowl = edges([(6, 13), (17, 13), (18, 14), (19, 15), (20, 17), (20, 20.5), (17.2, 20.5), (17.2, 17.2),
                  (5.8, 17.2), (5.8, 20.5), (3, 20.5), (3, 17), (4, 15)])

    def cowl_top(x, y):
        across = abs(x - ROD_AXIS_X) / 8.5
        return 7.6 - 2.2 * across * across - 1.2 * smoothstep(-3.0, -6.5, y)

    cushion("cowl", cowl, 0.0, cowl_top, grey, rounding=1.4)
    for side, outline in (("left", [(5.8, 17), (10, 17), (10, 23), (8, 23), (7.6, 20.2), (5.8, 20.2)]),
                          ("right", [(13, 17), (17.2, 17), (17.2, 20.2), (15.4, 20.2), (15, 23), (13, 23)])):
        cushion(f"red_{side}", edges(outline), 0.0, lambda x, y: 4.6, red, rounding=0.7)
    k.smooth(k.ellipsoid("lamp", (px(8), py(19), 4.4), (0.8, 1.0, 0.6), lamp, 12, 6), 60)
    # The lower flange (rows 24-26).
    round_part("flange_low", [(py(26.6), 4.6), (py(26.3), 5.3), (py(24.3), 5.5), (py(23.8), 4.6)], light,
               at=ROD_AXIS_X, z=ROD_Z, squash=ROD_SQUASH, floor=floor, power=2.6)
    for y in (py(12.5), py(22.5)):
        round_part(f"groove{y}", [(y - 0.35, 3.0), (y, 3.25), (y + 0.35, 3.0)], dark, at=ROD_AXIS_X, z=ROD_Z,
                   squash=ROD_SQUASH, floor=floor)


def rod_tail():
    grey = pal("rod_grey", 6, metallic=0.6, roughness=0.35)
    light = pal("rod_light", 9, metallic=0.6, roughness=0.3)
    dark = pal("rod_dark", 3, metallic=0.5, roughness=0.5)
    floor = 0.0
    # Half widths of the sprite's rows, from the top edge (continuing rod_top) to the point.
    body = [(14.0, 3.3), (py(1), 2.6), (py(3), 2.6), (py(4), 3.4), (py(7), 3.4), (py(8.5), 2.9), (py(10), 2.6),
            (py(12), 2.8), (py(13), 3.3), (py(17), 3.3), (py(18), 2.9), (py(19), 3.4), (py(21), 3.9), (py(23), 3.7),
            (py(24.5), 3.0), (py(25.5), 2.2), (py(26.5), 1.1), (py(27.3), 0.3)]
    round_part("body", sorted(body), grey, at=ROD_AXIS_X, z=ROD_Z, squash=ROD_SQUASH, floor=floor, segments=24)
    round_part("collar", [(py(2.6), 2.8), (py(2.4), 4.4), (py(1.6), 4.4), (py(1.4), 2.8)], light, at=ROD_AXIS_X,
               z=ROD_Z, squash=ROD_SQUASH, floor=floor, power=2.6)
    round_part("flange", [(py(16.6), 3.2), (py(16.3), 4.4), (py(14.3), 4.6), (py(13.8), 3.4)], light, at=ROD_AXIS_X,
               z=ROD_Z, squash=ROD_SQUASH, floor=floor, power=2.6)
    for y in (py(3.2), py(8.6), py(18.2)):
        round_part(f"groove{y}", [(y - 0.35, 2.7), (y, 3.05), (y + 0.35, 2.7)], dark, at=ROD_AXIS_X, z=ROD_Z,
                   squash=ROD_SQUASH, floor=floor)


# --- Building ------------------------------------------------------------------------------------

# name: (builder, [(sheet file, sprite)] its top view should match)
MODELS = {
    "fire_orb": (fire_orb, [("enemy_A", 277)]),
    "cell_sphere": (cell_sphere, [("enemy_3", 229), ("enemy_5", 89)]),
    "rod_top": (rod_top, [("enemy_5", 55)]),
    "rod_tail": (rod_tail, [("enemy_5", 93)]),
}


def main():
    options = k.args()
    only = options["only"].split(",") if "only" in options else None
    here = os.path.dirname(os.path.abspath(__file__))
    for name, (build, sprites) in MODELS.items():
        if only and name not in only:
            continue
        k.reset()
        build()
        if "sheets" in options:
            for sheet, index in sprites:
                print(f"== {name} vs {sheet} {index}")
                k.check_silhouette(os.path.join(options["sheets"], sheet + ".png"), index)
        bpy.context.view_layer.update()
        corners = [obj.matrix_world @ Vector(c) for obj in bpy.context.scene.objects if obj.type == "MESH"
                   for c in obj.bound_box]
        low = Vector([min(c[i] for c in corners) for i in range(3)])
        high = Vector([max(c[i] for c in corners) for i in range(3)])
        print(f"== {name} bounds {tuple(round(v, 2) for v in low)} .. {tuple(round(v, 2) for v in high)}")
        k.export(os.path.join(here, "..", "..", "..", "..", "assets", "models", "enemies", name + ".glb"))
        if "preview" in options:
            bpy.context.scene.view_settings.view_transform = "Standard"  # the palette's colours as they are
            k.preview(f"{options['preview']}_{name}", (W, H))


main()
