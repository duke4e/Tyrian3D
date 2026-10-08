"""Enemies of wave 1, batch C, facing the way their sprites do (models.cfg: yaw=0 unless noted):

- claw_gate_left / claw_gate_right (sheet 5 85 / 87): the two halves of the armoured claw gate of
  APPROACH and BRAINIAC, standing on the ground; a red arc joins them at the bottom.
- deli_arm_left / deli_arm_right (sheet T 39 / 49): the gun arms hanging from DELI's boss, ribbed red
  arms ending in pods with a glowing eye.
- stargate_top / stargate_bottom (sheet E 199 / 237): the two halves of STARGATE's glowing red crystal
  blades, standing on the ground.
- dome_gunship (sheet 2 91): the small grey gunship with a bronze dome, built nose up the screen; its
  eight frames are headings the level picks (models.cfg: yaw=velocity).
- orb_crimson (sheet K 195): a dark red glass orb with an ember glowing inside where the sprite has its
  bright spot (FLEET, STATION).
- purple_pod (sheet 5 47): a purple pod with a red strap and a golden clasp (HARVEST, LAVA RUN).
- spike_mine_teal (sheet A 167): a faceted teal mine with spikes all round, which turns.
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
from mathutils import Matrix, Vector, geometry

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


def smoothstep(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


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


def frame_rings(path, radii, segments=12, squash=1.0, up=(0, 0, 1)):
    """Cross-section rings along a path of points (tube, hose, claw): circles of the given radii
    perpendicular to the path, squash scaling them towards the up direction."""
    path = [Vector(p) for p in path]
    radii = radii if isinstance(radii, (list, tuple)) else [radii] * len(path)
    rings = []
    up = Vector(up)
    for i, p in enumerate(path):
        t = (path[min(i + 1, len(path) - 1)] - path[max(i - 1, 0)]).normalized()
        u = up if abs(t.dot(up)) < 0.95 else Vector((1, 0, 0))
        side = t.cross(u).normalized()
        upv = side.cross(t).normalized()
        r = radii[i]
        rings.append([p + side * math.cos(2 * math.pi * j / segments) * r +
                      upv * math.sin(2 * math.pi * j / segments) * r * squash for j in range(segments)])
    return rings


def tube(name, path, radii, mat, segments=12, squash=1.0, smooth=60):
    """A tube along a path (see frame_rings), its ends closed."""
    obj = k.loft(name, frame_rings(path, radii, segments, squash), mat)
    return k.smooth(obj, smooth)


def catmull(points, step=0.5):
    """A smooth path through points (3D), sampled about every step."""
    pts = [Vector(p) for p in points]
    out = []
    for i in range(len(pts) - 1):
        p0, p1, p2, p3 = pts[max(i - 1, 0)], pts[i], pts[i + 1], pts[min(i + 2, len(pts) - 1)]
        count = max(1, int(math.ceil((p2 - p1).length / step)))
        for j in range(count):
            t = j / count
            t2, t3 = t * t, t * t * t
            out.append(0.5 * (2 * p1 + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 +
                              (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
    out.append(pts[-1])
    return out


def cone(name, base, tip, radius, mat, vertices=10, tip_radius=0.0):
    base, tip = Vector(base), Vector(tip)
    axis = tip - base
    bpy.ops.mesh.primitive_cone_add(vertices=vertices, radius1=radius, radius2=tip_radius, depth=axis.length,
                                    location=(base + tip) / 2)
    obj = bpy.context.active_object
    obj.name = name
    obj.rotation_euler = axis.to_track_quat("Z", "Y").to_euler()
    obj.data.materials.append(mat)
    return obj


def bake_transforms():
    for obj in bpy.context.scene.objects:
        if obj.type == "MESH":
            obj.data.transform(obj.matrix_world)
            obj.matrix_world = Matrix.Identity(4)


def mirror_scene(offset=0.0):
    """Mirrors every mesh across x = 0, then moves it by offset along x (a model's mirror twin)."""
    bake_transforms()
    flip = Matrix.Translation((offset, 0, 0)) @ Matrix.Scale(-1, 4, (1, 0, 0))
    for obj in bpy.context.scene.objects:
        if obj.type == "MESH":
            obj.data.transform(flip)
            obj.data.flip_normals()


# --- Claw gate (sheet 5 85 and 87) ----------------------------------------------------------------
# h helmet (the outer armour with the eyes), p pauldron (the inner block's head), b the shoulder
# between them, l the outer leg, c its red claw, s the inner leg, f the red arc joining the halves.

GATE_LEFT = art("""
........................
........hhhhh....pppppp.
.....hhhhhhhh...pppppppp
....hhhhhhhhhbbbpppppppp
...hhhhhhhhhhbbbpppppppp
...hhhhhhhhhhbbbpppppppp
...hhhhhhhhhhbbbppppppp.
..hhhhhhhhhhhbbbbbbbbbb.
..hhhhhhhhhhhbbbbbbbbb..
..hhhhhhhhhhhbbbbbbbbb..
..hhhhhhhhhhhbbbbbbbbb..
..hhhhhhhhhhhbbbbbbbbb..
....lllllllll.bbbbssss..
....lllllllllll...ssss..
....llllllllll....ssss..
....llllllllll.....sss..
....lllllllllll....sss..
....lllllllllll....sss..
....lllllllllll...ssss..
....lllllllllll..sssss..
.....cccccllll...ssss...
.....cccccllll...sssff..
.....cccccc.......ffffff
.....cccccc........fffff
.......ccccc........ffff
........cccc.........fff
""")

GATE_RIGHT = art("""
........................
..pppppp....hhhhh.......
ppppppppp...hhhhhhhh....
pppppppppbbbhhhhhhhhh...
ppppppppbbbbhhhhhhhhhh..
ppppppppbbbbhhhhhhhhhh..
..ppppppbbbbhhhhhhhhhh..
..bbbbbb.bbbhhhhhh.hhhh.
...bbbbbbbbbhhhhhhhhhhh.
...bbbbbbbbbhhhhhhhhhhh.
...bbbbbbbbbhhhhhhhhhhh.
...bbbbbbbbbhhhhhhhhhhh.
...sssssbbb.lllllllll...
...ssss...lllllllllll...
...ssss....llllllllll...
...sss.....llllllllll...
...sss....lllllllllll...
...sss....lllllllllll...
...ssss...lllllllllll...
...sssss..lllllllllll...
....ssss...llllccccc....
...ffsss...llllccccc....
fffffff.......cccccc....
ffffff........cccccc....
fffff........ccccc......
ffff.........cccc.......
""")


def claw_gate(rows, side):
    """side 1: the left half (5 85), -1: the right half (5 87), which is drawn as the left's mirror
    one pixel to the right (column c there is column 24 - c here)."""
    k.reset()
    steel = k.material("gate_steel", palette=6, metallic=0.6, roughness=0.38)
    light = k.material("gate_light", palette=8, metallic=0.6, roughness=0.32)
    bright = k.material("gate_bright", palette=10, metallic=0.65, roughness=0.28)
    dark = k.material("gate_dark", palette=3, metallic=0.5, roughness=0.5)
    red = k.material("gate_red", palette=70, metallic=0.35, roughness=0.3)
    glow = k.material("gate_glow", palette=72, roughness=0.2, emission=(255, 60, 30), emission_strength=1.2)
    eye = k.material("gate_eye", palette=72, roughness=0.2, emission=(255, 40, 20), emission_strength=2.5)

    def col(c):  # a column of the left half as this half's x
        return px(c) if side > 0 else px(24 - c)

    seam = (lambda a, b: a[0] > 11.99 and b[0] > 11.99) if side > 0 else (lambda a, b: a[0] < -11.99 and b[0] < -11.99)

    def helmet(x, y, d):
        # A high back (rows 1-6), a face sloping down to the eyes (row 8) and a lower lip (rows 9-11).
        crown = 9.8 - 3.0 * smoothstep((py(6.0) - y) / (py(6.0) - py(9.4)))
        return round_edge(d, 3.0, crown, 2.2)

    # The armour, the shoulder and the legs.
    relief("helmet", outline(rows, "h"), helmet, light)
    relief("pauldron", outline(rows, "p"), lambda x, y, d: round_edge(d, 3.5, 11.0, 2.4), light)
    relief("shoulder", outline(rows, "b"), lambda x, y, d: round_edge(d, 2.5, 6.6, 1.6), steel)
    groove = col(9)
    relief("leg", outline(rows, "l"),
           lambda x, y, d: round_edge(d, 2.0, 6.2, 1.8) - 1.6 * math.exp(-((x - groove) / 0.55) ** 2), steel,
           spacing=0.45, lines=[[(groove + dx, 14.0), (groove + dx, -14.0)] for dx in (-0.9, -0.45, 0.0, 0.45, 0.9)])
    relief("shaft", outline(rows, "s"), lambda x, y, d: round_edge(d, 1.8, 5.2, 1.2), steel)
    # The claw, a hook thinning to its point (row 25).
    relief("claw", outline(rows, "c"),
           lambda x, y, d: round_edge(d, 0.6, 4.2 - 2.6 * smoothstep((py(19.5) - y) / 5.5), 1.8), red)
    relief("foot", outline(rows, "f"), lambda x, y, d: round_edge(d, 0.8, 3.2, 1.6), red, cut=seam)
    # The crest along the helmet, the ridge along the pauldron (the sprites' bright lines).
    crest = col(9) if side > 0 else col(9.5)
    k.smooth(k.lathe("crest", [(py(6.8), 0.1), (py(6.4), 0.6), (py(2.5), 0.75), (py(1.6), 0.2)], bright,
                     segments=12, axis_x=crest, axis_z=9.6, squash=0.9), 60)
    k.smooth(k.lathe("ridge", [(py(6.5), 0.1), (py(6), 0.8), (py(2.2), 0.9), (py(1.4), 0.2)], bright,
                     segments=12, axis_x=col(18.5), axis_z=10.8, squash=0.8), 60)
    # The two red eyes in the sloping face, a bright lip under them.
    for c in (7, 10):
        k.smooth(k.ellipsoid(f"eye{c}", (col(c), py(8.0), 8.0), (0.95, 0.8, 0.7), eye, 12, 6), 60)
    tube("lip", catmull([(col(4.4), py(10.2), 6.2), (col(8.5), py(10.4), 6.7), (col(12.6), py(10.2), 6.2)]),
         0.6, bright, squash=0.8)
    # The glowing red stripe on the inner leg.
    stripe = [(col(18), py(7.6)), (col(21), py(7.6)), (col(21), py(11.5)), (col(20.6), py(13.6)),
              (col(18.6), py(13.6)), (col(18), py(11.5))]
    if side < 0:
        stripe = stripe[::-1]
    relief("stripe", stripe, lambda x, y, d: round_edge(d, 5.6, 7.4, 1.0), glow, spacing=0.45, band=1.0)
    # Bolts on the pauldron and the shoulder.
    for c, r, z in ((20.5, 4.5, 10.6), (15, 9, 6.4)):
        k.smooth(k.ellipsoid(f"bolt{c}", (col(c), py(r), z), (0.6, 0.6, 0.4), dark, 10, 5), 60)


def claw_gate_left():
    claw_gate(GATE_LEFT, 1)


def claw_gate_right():
    claw_gate(GATE_RIGHT, -1)


# --- DELI's gun arms (sheet T 39 and 49) ----------------------------------------------------------
# The left arm comes down from the boss (the sprite's top edge), bends at a cuff to the right and
# ends in a pod with a glowing eye; the right arm (T 49) is its mirror one pixel to the left.

ARM_POD = art("""
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
.....################...
.......##############...
.......##############...
.......##############...
.......##############...
.......##############...
.......##############...
.......##############...
.......##############...
.......##############...
.......#############....
........###########.....
.........#########......
..........######........
""")


def deli_arm(side):
    k.reset()
    shell = k.material("arm_shell", palette=72, metallic=0.35, roughness=0.35)
    pale = k.material("arm_pale", palette=74, metallic=0.35, roughness=0.3)
    black = k.material("arm_black", palette=2, metallic=0.4, roughness=0.25)
    grey = k.material("arm_grey", palette=6, metallic=0.6, roughness=0.3)
    eye = k.material("arm_eye", palette=124, roughness=0.15, emission=(255, 200, 60), emission_strength=2.5)
    iris = k.material("arm_iris", palette=117, roughness=0.2, emission=(220, 20, 0), emission_strength=1.6)
    # The upper arm: a pleated tube from above the sprite's top down to the cuff.
    axis_x, axis_z, radius = px(9), 1.6, 6.4
    rings = []
    for i in range(13):
        y = 14.6 - i * 0.9
        ring = []
        for j in range(48):
            a = 2 * math.pi * j / 48
            pleat = 1 + 0.045 * math.cos(18 * a) if math.sin(a) > -0.2 else 1
            ring.append(Vector((axis_x + math.cos(a) * radius * pleat, y,
                                axis_z + math.sin(a) * radius * 0.72 * pleat)))
        rings.append(ring)
    k.smooth(k.loft("upper_arm", rings[::-1], shell), 70)
    # The cuff: the elbow, across to the pod.
    tube("cuff", catmull([(px(3.6), py(9.0), 2.6), (px(8), py(9.2), 4.6), (px(14), py(9.2), 4.8),
                          (px(18.2), py(9.6), 3.6)]), 2.3, pale, segments=20, squash=0.9)
    # The pod: rounded, a bright brow over the eye socket, a grey nozzle beside it.
    relief("pod", outline(ARM_POD), lambda x, y, d: round_edge(d, 1.2, 7.4, 4.6), shell,
           bottom=lambda x, y, d: -round_edge(d, 0.0, 3.0, 3.0), smooth=60, spacing=0.7, band=1.5, coarse=2)
    tube("brow", catmull([(px(8.2), py(13.4), 4.6), (px(10.5), py(13.2), 7.0), (px(13.5), py(13.0), 7.6),
                          (px(16.5), py(13.2), 7.0), (px(18.8), py(13.6), 4.8)]), 1.3, pale, segments=16, squash=0.75)
    ex, ey = px(13.8), py(18.8)
    k.smooth(k.ellipsoid("socket", (ex, ey, 6.6), (3.4, 2.9, 1.5), black, 24, 10), 60)
    k.smooth(k.ellipsoid("iris", (ex + 0.1, ey + 0.1, 7.3), (2.4, 2.1, 1.1), iris, 20, 10), 60)
    k.smooth(k.ellipsoid("eye", (ex - 0.3, ey + 0.5, 7.9), (1.1, 0.95, 0.75), eye, 16, 8), 60)
    tube("nozzle", [(px(10.8), py(19.6), 6.6), (px(8.2), py(19.8), 6.2)], 0.95, grey, segments=12)
    # The black hose beside the upper arm, from the boss down into the cuff.
    tube("hose", catmull([(px(19.0), 14.8, 2.2), (px(18.0), py(2.0), 2.8), (px(17.2), py(5.0), 3.2),
                          (px(16.4), py(8.0), 3.4)]), 1.75, black, segments=14, squash=0.8)
    if side < 0:
        mirror_scene(-1.0)


def deli_arm_left():
    deli_arm(1)


def deli_arm_right():
    deli_arm(-1)


# --- STARGATE's crystal blades (sheet E 199 above E 237) ------------------------------------------

BLADE_TOP = art("""
........................
...........####.........
.........########.......
.......############.....
......###############...
.....#################..
....###################.
...#############..#####.
...##############.#####.
...####################.
...##.##########.######.
...#############.######.
...#############.######.
...#############.######.
...#############.######.
...#############.######.
...#############.######.
...############..######.
...############..######.
...############..######.
...############..######.
...############..######.
...############..######.
...############..######.
...############..######.
...############..######.
...############..######.
...############..######.
""")

BLADE_BOTTOM = art("""
...############..######.
...############..######.
...############..######.
...############..######.
....##########...#####..
....##########...#####..
....##########...#####..
....##########...#####..
....##########...####...
....##########...####...
.....#########..#####...
.....#########..#####...
.....#########..####....
......########..####....
......########.#####....
.......############.....
.......############.....
.......###########......
........##########......
........#########.......
.........########.......
.........#######........
..........######........
..........#####.........
...........####.........
...........###..........
............#...........
""")


def stargate_blade(top_half):
    """The blade stands on the ground: a ridge along its middle, facets down to its edges, a slit
    near its right edge; its spine and edges glow. Built in the coordinates of both sprites (Y, 0 at
    the seam), so the halves meet."""
    k.reset()
    body = k.material("blade_body", palette=113, metallic=0.2, roughness=0.15, emission=(110, 6, 0),
                      emission_strength=0.35)
    ember = k.material("blade_ember", palette=119, roughness=0.25, emission=(255, 70, 10), emission_strength=1.6)
    hot = k.material("blade_hot", palette=123, roughness=0.2, emission=(255, 190, 70), emission_strength=2.6)
    shift = 14.0 if top_half else -14.0
    rows = BLADE_TOP if top_half else BLADE_BOTTOM
    spine = 0.5
    arch = [(-5.5, 17.6), (spine, 19.8), (3.6, 19.0)]  # the inner arch's glowing rib (Y)

    def height(x, y, d):
        tent = 9.0 - 0.62 * abs(x - spine)
        return round_edge(d, 1.2, tent, 2.2)

    def pick(x, y, z, d):
        # The spine glows, hot where the sprite's is brightest; so do the inner arch's rib and the
        # edges on the left and round the arch.
        Y = y + shift
        if abs(x - spine) < 0.5:
            return 2 if 7.0 < Y < 21.5 or Y < -18.0 else 1
        if min(_seg_dist(x, Y, a, b) for a, b in zip(arch, arch[1:])) < 0.45:
            return 1
        if d < rim and (x < spine - 1.5 or Y > 20.0):
            return 2 if Y < -17.0 else 1
        return 0

    rim = 0.65
    outline_poly = s.outline(rows, 24, 1.1)
    cut = (lambda a, b: a[1] < -13.99 and b[1] < -13.99) if top_half else (lambda a, b: a[1] > 13.99 and b[1] > 13.99)
    lines = [[(x, -14.5), (x, 14.5)] for x in (spine - 0.5, spine, spine + 0.5)]
    for off in (-0.45, 0.45):
        lines.append([(ax, ay - shift + off) for ax, ay in arch])
    lines += inset_lines(outline_poly, rim, cut)
    relief("blade", outline_poly, height, [body, ember, hot], spacing=0.45, cut=cut, mat_fn=pick, smooth=35,
           band=2.8, lines=lines)


def inset_lines(polygon, distance, cut=None):
    """The outline moved inwards by distance (counter-clockwise polygon), as polylines: points that
    come closer than that to another part of the outline (narrow places) are left out, and so are
    the edges where cut(a, b) is true."""
    n = len(polygon)
    keep = []
    for i in range(n):
        p0, p1, p2 = Vector(polygon[i - 1]), Vector(polygon[i]), Vector(polygon[(i + 1) % n])
        if cut and cut(polygon[i - 1], polygon[i]) and cut(polygon[i], polygon[(i + 1) % n]):
            keep.append(None)
            continue
        n0 = Vector((-(p1 - p0).y, (p1 - p0).x)).normalized()  # inward normals (counter-clockwise)
        n1 = Vector((-(p2 - p1).y, (p2 - p1).x)).normalized()
        bis = (n0 + n1)
        if bis.length < 1e-6:
            keep.append(None)
            continue
        bis.normalize()
        q = p1 + bis * distance / max(0.35, bis.dot(n1))
        near = min(_seg_dist(q.x, q.y, polygon[j], polygon[(j + 1) % n]) for j in range(n))
        keep.append((q.x, q.y) if near > distance * 0.8 and _inside(q.x, q.y, polygon) else None)
    lines, run = [], []
    for q in keep + keep[:1]:
        if q is None:
            if len(run) > 1:
                lines.append(run)
            run = []
        else:
            run.append(q)
    if len(run) > 1:
        lines.append(run)
    return lines


def stargate_top():
    stargate_blade(True)


def stargate_bottom():
    stargate_blade(False)


# --- The dome gunship (sheet 2 91, built as its frame 45, nose up the screen) ----------------------

GUNSHIP_HULL = art("""
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
......###########.......
.....#############......
.....#############......
.....#############......
.....#############......
.....#############......
.....#############......
......###########.......
.......###...###........
""")


def dome_gunship():
    k.reset()
    hull = k.material("gunship_hull", palette=6, metallic=0.6, roughness=0.32)
    light = k.material("gunship_light", palette=8, metallic=0.6, roughness=0.3)
    dark = k.material("gunship_dark", palette=3, metallic=0.5, roughness=0.45)
    bronze = k.material("gunship_bronze", palette=23, metallic=0.8, roughness=0.25)
    tip = k.material("gunship_tip", palette=25, metallic=0.8, roughness=0.25)
    red = k.material("gunship_red", palette=116, roughness=0.2, emission=(255, 30, 10), emission_strength=2.2)
    relief("hull", outline(GUNSHIP_HULL), lambda x, y, d: round_edge(d, 1.0, 3.6, 2.6), hull,
           bottom=lambda x, y, d: -round_edge(d, 0.0, 1.6, 2.6), smooth=60, spacing=0.6, band=1.2, coarse=2)
    # The two forward prongs either side of the gun.
    for x in (-3.1, 2.2):
        k.smooth(k.lathe(f"prong{x}", [(1.5, 1.7), (6.4, 1.8), (7.4, 1.4), (8.0, 0.5)], light, segments=16,
                         axis_x=x, axis_z=1.5, squash=0.8), 60)
    # The gun: a grey barrel with a bronze muzzle, from the dome forward.
    gun_x, gun_z = -0.5, 3.6
    k.smooth(k.lathe("barrel", [(1.0, 1.0), (7.6, 0.75), (8.0, 0.75)], dark, segments=12, axis_x=gun_x,
                     axis_z=gun_z, squash=0.9), 60)
    k.smooth(k.lathe("muzzle", [(7.9, 0.95), (11.2, 0.95), (11.8, 0.7), (12.0, 0.2)], tip, segments=12,
                     axis_x=gun_x, axis_z=gun_z, squash=0.9), 60)
    # The bronze dome on a dark ring, the red light at the back.
    k.smooth(k.ellipsoid("ring", (-0.5, 0.8, 3.3), (3.3, 2.9, 0.7), dark, 24, 8), 60)
    k.smooth(k.ellipsoid("dome", (-0.5, 0.9, 3.5), (2.8, 2.5, 2.4), bronze, 24, 12), 60)
    k.smooth(k.ellipsoid("light", (0.5, py(17.4), 2.9), (1.5, 0.9, 0.9), red, 12, 6), 60)
    # Vents along the sides.
    for x in (-5.0, 4.0):
        k.box(f"vent{x}", (x, -1.0, 2.2), (0.8, 3.6, 0.6), dark)


# --- Round ones ------------------------------------------------------------------------------------

def orb_crimson():
    """A dark red glass orb with an ember glowing inside (K 195), where the sprite has its bright spot."""
    k.reset()
    glass = k.material("orb_crimson_glass", palette=114, metallic=0.1, roughness=0.05, alpha=0.72)
    core = k.material("orb_crimson_core", palette=113, roughness=0.4, emission=(130, 8, 0), emission_strength=0.7)
    halo = k.material("orb_crimson_halo", palette=120, roughness=0.3, emission=(255, 90, 10), emission_strength=2.4)
    ember = k.material("orb_crimson_ember", palette=125, roughness=0.3, emission=(255, 230, 130),
                       emission_strength=4.0)
    c = (0.5, 1.5, 0.0)
    k.smooth(k.ellipsoid("core", c, (9.2, 9.2, 8.8), core, 32, 16), 70)
    k.smooth(k.ellipsoid("halo", (c[0] - 3.2, c[1] + 2.8, 5.9), (3.2, 3.2, 2.4), halo, 20, 10), 70)
    k.smooth(k.ellipsoid("ember", (c[0] - 3.3, c[1] + 2.9, 7.2), (1.6, 1.6, 1.2), ember, 16, 8), 70)
    k.smooth(k.ellipsoid("orb", c, (10.4, 10.4, 10.0), glass, 40, 20), 70)


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


def spike_mine_teal():
    """A faceted teal mine with eight spikes round its middle and more above and below (A 167); it
    turns (models.cfg: spin)."""
    k.reset()
    ball = k.material("tealmine_ball", palette=215, metallic=0.55, roughness=0.25)
    tips = k.material("tealmine_spikes", palette=219, metallic=0.6, roughness=0.2)
    c = Vector((-0.5, 0.5, 8.4))
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=8.5, location=tuple(c))
    core = bpy.context.active_object
    core.name = "ball"
    core.data.materials.append(ball)
    k.smooth(core, 15)
    spikes = [(a, 0.0, 11.8) for a in range(0, 360, 45)]
    spikes += [(a + 22.5, 45.0, 11.4) for a in range(0, 360, 90)]
    spikes += [(a + 67.5, -45.0, 11.4) for a in range(0, 360, 90)]
    spikes += [(0.0, 90.0, 11.4)]
    for i, (az, el, length) in enumerate(spikes):
        a, e = math.radians(az), math.radians(el)
        d = Vector((math.cos(e) * math.cos(a), math.cos(e) * math.sin(a), math.sin(e)))
        cone(f"spike{i}", c + d * 7.0, c + d * length, 1.7, tips, vertices=8, tip_radius=0.35)


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
    "claw_gate_left": (claw_gate_left, "5", 85),
    "claw_gate_right": (claw_gate_right, "5", 87),
    "deli_arm_left": (deli_arm_left, "T", 39),
    "deli_arm_right": (deli_arm_right, "T", 49),
    "stargate_top": (stargate_top, "E", 199),
    "stargate_bottom": (stargate_bottom, "E", 237),
    "dome_gunship": (dome_gunship, "2", 45),
    "orb_crimson": (orb_crimson, "K", 195),
    "purple_pod": (purple_pod, "5", 47),
    "spike_mine_teal": (spike_mine_teal, "A", 167),
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
