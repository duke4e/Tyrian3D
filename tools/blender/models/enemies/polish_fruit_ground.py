"""FRUIT's machines on its honeycomb floor (sheet %, written x25 in models.cfg; 2x2 sprites of episode 5, ground
enemies), polished (2026-10-22, round 35; they replace wave3_al.py and wave3_al_ball.py: the geodesic ball, the
pillars, the orb in its cup, the glyph tree and hook, the ice crystal and the glass capsule).

(Full description: DOC below.)
"""
import itertools
import math
import os
import sys

import bmesh
import bpy
from mathutils import Matrix, Quaternion, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
import polish_machine_kit as mk  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402
from polish_deli_boss import join, drop_unused  # noqa: E402
from polish_coral_manta import cut  # noqa: E402
from polish_torm_beetle import tube  # noqa: E402
from polish_fruit_pods import stations, ribbon  # noqa: E402
from polish_pineapple import section_loft, paint_light, shear_to_camera, smoothstep, light_value, LIGHT  # noqa: E402

VIEW_TILT = 20.0
TAN_T = math.tan(math.radians(VIEW_TILT))
TOWARDS_VIEW = Vector((0.0, -math.sin(math.radians(VIEW_TILT)), math.cos(math.radians(VIEW_TILT))))
SOCKET_C = (0.0, -7.0)            # the map's socket's middle in a sprite (columns 4-19, rows 14-27)


def mat(m, key, index, metallic=0.3, roughness=0.4, glow=0.0, alpha=None):
    if key not in m:
        pal = k.level_palette()
        extra = dict(emission=pal[index], emission_strength=glow) if glow > 0 else {}
        if alpha is not None:
            extra["alpha"] = alpha
        m[key] = k.material(f"fground_{key}", palette=index, metallic=metallic, roughness=roughness, **extra)
    return m[key]


def oblique(objects, K):
    """Shears upright parts into the picture's plane: y += K z (the sprites draw upright things leaning up the screen,
    K pixels up for each pixel of height; shear_to_camera later takes the camera's own tan 20 off again)."""
    for obj in objects:
        mesh = obj.data
        had = mesh.has_custom_normals
        normals = [Vector(cn.vector) for cn in mesh.corner_normals] if had else None
        for v in mesh.vertices:
            v.co.y += v.co.z * K
        if had:
            mesh.normals_split_custom_set([tuple(Vector((n.x, n.y, n.z - K * n.y)).normalized()) for n in normals])
        mesh.update()


def prism(name, verts2d, z0, z1, mtl):
    """A polygon (counter-clockwise) extruded from z0 to z1, closed."""
    n = len(verts2d)
    verts = [Vector((x, y, z0)) for x, y in verts2d] + [Vector((x, y, z1)) for x, y in verts2d]
    faces = [tuple(range(n - 1, -1, -1)), tuple(range(n, 2 * n))]
    for i in range(n):
        j = (i + 1) % n
        faces.append((i, j, n + j, n + i))
    obj = k.mesh_object(name, verts, faces, mtl)
    k.recalc_normals(obj)
    return obj


def hexagon(cx, cy, r, phase=0.0):
    return [(cx + r * math.cos(math.radians(phase + 60 * i)), cy + r * math.sin(math.radians(phase + 60 * i)))
            for i in range(6)]


def rounded_square(cx, cy, hw, hd, r, steps=3):
    pts = []
    for qx, qy, a0 in ((1, 1, 0), (-1, 1, 90), (-1, -1, 180), (1, -1, 270)):
        ccx, ccy = cx + qx * (hw - r), cy + qy * (hd - r)
        for i in range(steps + 1):
            a = math.radians(a0 + 90 * i / steps)
            pts.append((ccx + r * math.cos(a), ccy + r * math.sin(a)))
    return pts


def lathe_z(name, profile, centre, mtl, segments=32):
    """mk.lathe (a round part about a vertical axis at centre: profile [(radius, z)] from its bottom up)."""
    obj = mk.lathe(name, profile, centre, mtl, segments=segments)
    k.recalc_normals(obj)
    return obj


def axis_lathe(name, profile, start, direction, mtl, segments=24):
    """A round part about an axis from start along direction: profile [(t, radius)]; ends closed."""
    rings = [[Vector((r * math.cos(2 * math.pi * j / segments), r * math.sin(2 * math.pi * j / segments), t))
              for j in range(segments)] for t, r in profile[1:-1]]
    obj = k.loft(name, rings, mtl, start_point=(0, 0, profile[0][0]), end_point=(0, 0, profile[-1][0]))
    rot = Vector((0, 0, 1)).rotation_difference(Vector(direction).normalized()).to_matrix().to_4x4()
    obj.data.transform(Matrix.Translation(start) @ rot)
    k.recalc_normals(obj)
    return obj


# --- The geodesic ball (% 191 193 above 229 231) --------------------------------------------------------------------
BALL_C = Vector((0.5, 0.5, 3.5))  # its middle (columns 1-47, rows 4-50 of the 48 x 56 picture), sunk into the ground
BALL_R = 23.5
PATTERN_AT = -9.0                 # the top pentagon's middle: degrees from straight up, up the screen (+) or down
STRETCH = 1.22                    # the sprites draw the panels larger than a football's: angles from it stretched
PHI = (1 + 5 ** 0.5) / 2
FRAME_HW = 0.62                   # the frame's ribs: half-width of the gap they fill, their radius
RIB_R = 0.66
PANEL_DOME = 0.6


def pattern_top():
    a = math.radians(PATTERN_AT)
    return Vector((0.0, math.sin(a), math.cos(a)))


def warp(d):
    top = pattern_top()
    d = d.normalized()
    a = top.angle(d) if (d - top).length > 1e-9 else 0.0
    if a < 1e-6 or a > math.pi - 1e-3:
        return d
    axis = top.cross(d).normalized()
    return (Quaternion(axis, min(a * STRETCH, math.pi - 1e-3) - a) @ d).normalized()


def truncated_icosahedron():
    """The football's pattern on the unit sphere, turned so that a pentagon's middle is pattern_top() with a seam
    running down the screen from its lowest corner: faces [(kind, centre, corners)], edges [(a, b)]."""
    ico = [Vector(p) for s1 in (-1, 1) for s2 in (-1, 1)
           for p in ((0, s1, s2 * PHI), (s1, s2 * PHI, 0), (s2 * PHI, 0, s1))]
    near = {i: [j for j in range(12) if j != i and abs((ico[i] - ico[j]).length - 2.0) < 1e-6] for i in range(12)}
    tris = [t for t in itertools.combinations(range(12), 3)
            if all(abs((ico[a] - ico[b]).length - 2.0) < 1e-6 for a, b in itertools.combinations(t, 2))]
    target = pattern_top()
    q1 = ico[0].normalized().rotation_difference(target)
    nb = (q1 @ ico[near[0][0]]).normalized()

    def flat(vv):
        return (vv - target * vv.dot(target)).normalized()
    down = flat(Vector((0.0, -1.0, 0.0)))
    cur = flat(nb)
    ang = math.atan2(cur.cross(down).dot(target), cur.dot(down))
    q = Quaternion(target, ang) @ q1
    pts = [q @ p for p in ico]

    def third(a, b, t):
        return pts[a] + (pts[b] - pts[a]) * t
    faces, edges = [], []
    for i in range(12):
        corners = [third(i, j, 1 / 3) for j in near[i]]
        faces.append(("pent", corners))
        c = sum(corners, Vector()) / 5
        ref = (corners[0] - c).normalized()
        axis = c.normalized()
        corners.sort(key=lambda p: math.atan2(axis.dot(ref.cross(p - c)), ref.dot(p - c)))
        for a_, b_ in zip(corners, corners[1:] + corners[:1]):
            edges.append((a_, b_))
    for a, b, c_ in tris:
        corners = [third(a, b, 1 / 3), third(a, b, 2 / 3), third(b, c_, 1 / 3), third(b, c_, 2 / 3),
                   third(c_, a, 1 / 3), third(c_, a, 2 / 3)]
        faces.append(("hex", corners))
    for a, b in itertools.combinations(range(12), 2):
        if b in near[a]:
            edges.append((third(a, b, 1 / 3), third(a, b, 2 / 3)))
    out = []
    for kind, corners in faces:
        c = sum(corners, Vector()) / len(corners)
        axis = c.normalized()
        ref = (corners[0] - c).normalized()
        corners = sorted(corners, key=lambda p: math.atan2(axis.dot(ref.cross(p - c)), ref.dot(p - c)))
        scale = 1.0 / corners[0].length
        out.append((kind, c * scale, [p * scale for p in corners]))
    scale = 1.0 / edges[0][0].length
    return out, [(a * scale, b * scale) for a, b in edges]


def ball_point(d, r):
    return BALL_C + warp(d) * r


def panel(name, centre, corners, mtl_fn, rings=4, per_edge=4):
    """A glass panel: the face's polygon inset from its edges, on the sphere, domed, a skirt down into the ball."""
    n = len(corners)
    c = centre
    pull = FRAME_HW / BALL_R / math.cos(math.pi / n)
    inner = [c + (p - c) * (1.0 - pull / (p - c).length) for p in corners]
    outline = []
    for i in range(n):
        a, b = inner[i], inner[(i + 1) % n]
        for j in range(per_edge):
            outline.append(a + (b - a) * (j / per_edge))
    bm = bmesh.new()

    def place(p, s):
        return ball_point(p, BALL_R + PANEL_DOME * (1.0 - s * s) - 0.3 * smoothstep(0.75, 1.0, s))
    mid = bm.verts.new(place(c, 0.0))
    prev = None
    for i in range(1, rings + 1):
        s = i / rings
        ring = [bm.verts.new(place(c + (p - c) * s, s)) for p in outline]
        if prev is None:
            for j in range(len(ring)):
                bm.faces.new((mid, ring[j], ring[(j + 1) % len(ring)]))
        else:
            for j in range(len(ring)):
                jn = (j + 1) % len(ring)
                bm.faces.new((prev[j], ring[j], ring[jn], prev[jn]))
        prev = ring
    low = [bm.verts.new(BALL_C + (v.co - BALL_C).normalized() * (BALL_R - 1.2)) for v in prev]
    for j in range(len(prev)):
        jn = (j + 1) % len(prev)
        bm.faces.new((prev[j], low[j], low[jn], prev[jn]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    obj.data.materials.append(mtl_fn)
    k.recalc_normals(obj)
    k.smooth(obj, 60)
    return obj


def clip_below(obj, z=0.0):
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-6, plane_co=(0, 0, z),
                           plane_no=(0, 0, 1), clear_inner=True)
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()
    return obj


def geoball(m):
    faces, edges = truncated_icosahedron()
    glass = [mat(m, f"ball{i:x}", 0x30 + i, 0.35, 0.12, 0.06 + 0.012 * (i - 7)) for i in (7, 9, 10, 11, 12)]
    glint = mat(m, "ball_glint", 0x3e, 0.2, 0.08, 0.3)
    frame = mat(m, "ball_frame", 0x3c, 0.55, 0.22, 0.05)
    frame_dark = mat(m, "ball_frame_dark", 0x39, 0.5, 0.3)
    core = mat(m, "ball_core", 0x33, 0.3, 0.5)
    sun = LIGHT
    half = (sun + TOWARDS_VIEW).normalized()       # where the sun's glints sit (the mirror direction)
    parts = []
    inner = k.ellipsoid("ball_core", tuple(BALL_C), (BALL_R - 0.9,) * 3, core, 40, 20)
    parts.append(clip_below(k.smooth(inner, 60)))
    count = 0
    for kind, c, corners in faces:
        if max(ball_point(p, BALL_R).z for p in corners) < -0.3:
            continue
        obj = panel(f"ball_panel{count}", c, corners, glass[2])
        count += 1
        # painted by the light it gets (the pentagons a shade lighter), a glint where the sun shines back
        mesh = obj.data
        values = []
        for v in mesh.vertices:
            n = (v.co - BALL_C).normalized()
            values.append(light_value(n, 6.3 + (0.5 if kind == "pent" else 0.0), 3.4, 1.4))
        from polish_orb_red import band_split
        band_split(obj, values, [(-99, glass[0]), (5.0, glass[1]), (5.9, glass[2]), (6.7, glass[3]), (7.4, glass[4])])
        mk.paint(obj, lambda cc, nn: glint if (cc - BALL_C).normalized().dot(half) > 0.985 else None)
        parts.append(clip_below(obj))
    for i, (a, b) in enumerate(edges):
        pa, pb = ball_point(a, BALL_R + 0.05), ball_point(b, BALL_R + 0.05)
        if pa.z < -1.0 and pb.z < -1.0:
            continue
        pts = [ball_point(a + (b - a) * (j / 6), BALL_R + 0.05) for j in range(7)]
        rib = mk.tube(f"ball_rib{i}", pts, RIB_R, frame, 8)
        k.smooth(rib, 60)
        paint_light(rib, {"d": frame_dark, "f": frame}, [(-99, "d"), (5.6, "f")], 6.4)
        parts.append(clip_below(rib))
    return parts


# --- The pillars (% 205: its drum on its right, 243: on its left) ------------------------------------------------------
PILLAR_C = (0.0, -6.0)            # its foot's middle (in the map's socket)
PILLAR_HW = 3.7                   # half its width (columns 8-15)
PILLAR_H = 22.0                   # its height
PILLAR_RISE = 20.2                # how far up the screen the sprites draw its front face (row 22.5 to row 3)
DRUM = (13.0, 4.4, 3.7, 11.6)     # the drum: its axis' height, radius, from x to x (the right one's)


def pillar(m, side):
    steel = {key: mat(m, key, idx, 0.45, rough) for key, idx, rough in
             (("p5", 0x65, 0.4), ("p7", 0x67, 0.36), ("p9", 0x69, 0.32), ("pb", 0x6b, 0.3))}
    grey = {key: mat(m, key, idx, 0.55, rough) for key, idx, rough in
            (("g6", 0x06, 0.36), ("g8", 0x08, 0.32), ("ga", 0x0a, 0.28), ("gc", 0x0c, 0.24))}
    cx, cy = PILLAR_C
    hw, h = PILLAR_HW, PILLAR_H
    parts = []
    body = mk.prism("pillar", rounded_square(cx, cy, hw, hw, 0.9, 3), 0.0, h, steel["p7"])
    mk.bevel(body, 0.35, 2, 40)
    parts.append(body)
    # collars at its foot and under its end, a cap on its top
    for z0, z1, grow in ((0.0, 1.7, 0.6), (h - 3.4, h - 2.0, 0.45)):
        c = mk.prism(f"collar{z0:.0f}", rounded_square(cx, cy, hw + grow, hw + grow, 1.1, 3), z0, z1, steel["p5"])
        mk.bevel(c, 0.3, 2, 40)
        parts.append(c)
    cap = mk.prism("cap", rounded_square(cx, cy, hw - 0.8, hw - 0.8, 0.8, 3), h - 0.1, h + 0.6, steel["p9"])
    mk.bevel(cap, 0.25, 2, 40)
    parts.append(cap)
    for p in parts:
        k.smooth(p, 35)
        paint_light(p, steel, [(-99, "p5"), (5.6, "p7"), (6.6, "p9"), (7.4, "pb")], 6.5)
    # the drum: a grey barrel on a short arm, its axis across the screen, a seam round its middle, an electrode at
    # its outer end (the bolts leave from it)
    zd, rd, x0, x1 = DRUM
    sx = side
    arm = axis_lathe("arm", [(0.0, 0.01), (0.02, 2.0), (1.4, 2.0), (1.9, 1.6), (2.0, 0.01)],
                     Vector((sx * (hw - 0.4), cy, zd)), (sx, 0, 0), grey["g6"], 16)
    length = x1 - x0
    prof = [(0.0, 0.01), (0.02, rd - 1.2), (0.35, rd - 0.35), (0.9, rd), (length / 2 - 0.5, rd), (length / 2 - 0.15, rd - 0.55),
            (length / 2 + 0.15, rd - 0.55), (length / 2 + 0.5, rd), (length - 0.9, rd), (length - 0.35, rd - 0.35),
            (length - 0.02, rd - 1.2), (length, 0.01)]
    drum = axis_lathe("drum", prof, Vector((sx * x0, cy, zd)), (sx, 0, 0), grey["g8"], 28)
    tip = axis_lathe("electrode", [(0.0, 0.01), (0.02, 1.5), (0.6, 1.3), (1.4, 0.5), (1.6, 0.01)],
                     Vector((sx * (x1 - 0.1), cy, zd)), (sx, 0, 0), grey["gc"], 14)
    for p in (arm, drum, tip):
        k.smooth(p, 45)
        paint_light(p, grey, [(-99, "g6"), (5.6, "g8"), (6.7, "ga"), (7.5, "gc")], 6.8)
        parts.append(p)
    return parts


# --- The orb in its cup (% 233; frames 235 237) ---------------------------------------------------------------------------
CUP = (5.0, 3.0)                  # its radius, its rim's height
ORB_R = 2.35
ORB_AT = (0.0, -4.2, 2.7)         # the orb's middle in the picture's plane (the sprites' rows 16-19)
# per frame: the orb's body, its hot side, its hot spot (palette indices of ramp 15, its reds to golds) and glows
ORB_FRAMES = {233: ((0xf5, 0.3), (0xf7, 0.4), (0xf8, 0.48)), 235: ((0xf7, 0.36), (0xf9, 0.46), (0xfb, 0.54)),
              237: ((0xf9, 0.42), (0xfb, 0.52), (0xfd, 0.6))}


def hex_eye(m, frame):
    cx, cy = SOCKET_C
    r, hgt = CUP
    grey = {key: mat(m, key, idx, 0.6, rough) for key, idx, rough in
            (("g3", 0x03, 0.4), ("g6", 0x06, 0.36), ("g8", 0x08, 0.32), ("ga", 0x0a, 0.28), ("gc", 0x0c, 0.24))}
    dark = mat(m, "cup_inside", 0x01, 0.2, 0.6)
    prof = [(r + 0.2, -0.3), (r + 0.25, 0.4), (r, hgt - 0.7), (r - 0.15, hgt - 0.1), (r - 0.55, hgt + 0.08),
            (r - 0.95, hgt - 0.15), (r - 1.05, hgt - 0.8), (r - 1.4, 0.9), (r - 2.4, 0.6), (0.01, 0.5)]
    cup = lathe_z("cup", prof, (cx, cy), grey["g8"], 40)
    k.smooth(cup, 45)
    paint_light(cup, grey, [(-99, "g3"), (5.2, "g6"), (6.2, "g8"), (7.0, "ga"), (7.6, "gc")], 6.6)
    mk.paint(cup, lambda c, n: dark if math.hypot(c.x - cx, c.y - cy) < r - 0.9 and c.z < hgt - 0.4 else None)
    (b, bg), (s, sg), (h, hg) = ORB_FRAMES[frame]
    body = mat(m, f"orb{frame}", b, 0.0, 0.18, bg)
    side = mat(m, f"orb_side{frame}", s, 0.0, 0.14, sg)
    hot = mat(m, f"orb_hot{frame}", h, 0.0, 0.1, hg)
    ox, oy, oz = ORB_AT
    orb = mk.ball("orb", (ox, oy, oz), (ORB_R, ORB_R, ORB_R * 0.95), body, segments=24, rings=12, angle=80)
    hot_dir = Vector((0.45, 0.35, 1.0)).normalized()      # the sprites' hottest pixels at its upper right

    def pick(c, n):
        rel = (c - Vector(ORB_AT)).normalized()
        if rel.dot(hot_dir) > 0.86:
            return hot
        if rel.dot(TOWARDS_VIEW) > 0.55:
            return side
        return None
    mk.paint(orb, pick)
    return [cup, orb]


# --- The glyph tiles (% 269 267 153: the tree; 275 273 271: the hook) ---------------------------------------------------
# Their strokes (pixel paths, polish_fruit_pods.stations' way) and per frame (stroke palette index, glow; halo or None).
TREE = [[(9, 18), (10, 19), (11, 20)], [(13, 18), (12, 19), (11, 20)], [(11, 20), (11, 21), (11, 22)],
        [(11, 22), (10, 23)], [(11, 22), (12, 23), (13, 23)], [(13, 20), (14, 20)]]
TREE_DOTS = [(11, 18), (9, 20)]
HOOK = [[(11, 23), (11, 22), (10, 22), (9, 21), (9, 20), (9, 19), (10, 18), (11, 18), (12, 18), (13, 19), (14, 20),
         (14, 21)]]
GLYPH_FRAMES = {
    269: ((0x22, 0.12), None), 267: ((0x26, 0.32), ((0x3c, 0.2, 0.26, 1.0), (0x3b, 0.12, 0.15, 1.6))),
    153: ((0x2c, 0.5), ((0x3c, 0.34, 0.36, 1.1), (0x3c, 0.2, 0.2, 1.8))),
    275: ((0x71, 0.16), None), 273: ((0x76, 0.36), ((0x3c, 0.2, 0.26, 1.0), (0x3b, 0.12, 0.15, 1.6))),
    271: ((0x7c, 0.5), ((0x3c, 0.34, 0.36, 1.1), (0x3c, 0.2, 0.2, 1.8))),
}
STROKE_W, STROKE_H, STROKE_Z = (0.36, 0.48, 0.36), (0.22, 0.3, 0.22), 0.16


def glyph(m, strokes, dots, frame):
    (index, glow), halos = GLYPH_FRAMES[frame]
    stroke = mat(m, f"glyph{frame}", index, 0.2, 0.15, glow)
    parts = []
    paths = [list(s) for s in strokes] + [[(c - 0.35, r), (c + 0.35, r)] for c, r in dots]
    for i, path in enumerate(paths):
        obj = tube(f"stroke{i}", stations(path, STROKE_W, STROKE_H, STROKE_Z), stroke, segments=10)
        k.smooth(obj, 70)
        parts.append(obj)
    if halos:
        for j, (h_index, h_glow, alpha, hw) in reversed(list(enumerate(halos))):
            hm = mat(m, f"glyph_halo{frame}_{j}", h_index, 0.0, 0.5, h_glow, alpha)
            for i, path in enumerate(paths):
                parts.append(ribbon(f"halo{j}_{i}", path, hw, 0.12 + 0.02 * (1 - j), hm))
    return parts


# --- The ice crystal (% 201 above 239) and the glass capsule (% 169 above 207) -----------------------------------------
# Each stands in the map's socket in the lower sprite (its middle (0, -21) of the 24 x 56 picture: the pieces' origins
# (0, 14) and (0, -14)), upright, and leans up the screen as the sprites draw it (oblique: its top RISE pixels further up).
CRYSTAL = dict(foot=(0.0, -21.0), r=3.1, h=28.0, rise=29.5, point=6.2)
CAPSULE = dict(foot=(0.0, -20.5), r=8.0, h=20.0, rise=21.0)


def crystal(m):
    ice = {key: mat(m, key, idx, 0.15, rough, glow) for key, idx, rough, glow in
           (("i7", 0x87, 0.12, 0.12), ("i9", 0x89, 0.08, 0.16), ("ib", 0x8b, 0.06, 0.22), ("id", 0x8d, 0.05, 0.3),
            ("if", 0x8f, 0.05, 0.4))}
    fx, fy = CRYSTAL["foot"]
    r, h, pt = CRYSTAL["r"], CRYSTAL["h"], CRYSTAL["point"]
    parts = []
    # six faces, corners left and right; a pointed end
    hexa = hexagon(fx, fy, r, 0.0)
    rings = [[Vector((x, y, z)) for x, y in hexa] for z in (-0.3, h - pt)]
    body = k.loft("crystal", rings, ice["i9"], start_point=(fx, fy, -0.3), end_point=(fx, fy, h))
    parts.append(body)
    # two small shards at its foot, leaning out
    for i, (dx, lean, ln, rr) in enumerate(((-2.4, -26.0, 8.0, 1.25), (2.3, 22.0, 6.5, 1.05))):
        hx = hexagon(0.0, 0.0, rr, 0.0)
        rings = [[Vector((x, y, z)) for x, y in hx] for z in (-1.0, ln - 2.0)]
        shard = k.loft(f"shard{i}", rings, ice["i9"], start_point=(0, 0, -1.0), end_point=(0, 0, ln))
        shard.data.transform(Matrix.Translation((fx + dx, fy - 0.6, 0.0)) @ Matrix.Rotation(math.radians(lean), 4, "Y") @
                             Matrix.Rotation(math.radians(-14), 4, "X"))
        parts.append(shard)
    for p in parts:
        k.recalc_normals(p)
        k.smooth(p, 20)
        paint_light(p, ice, [(-99, "i7"), (5.5, "i9"), (6.5, "ib"), (7.3, "id"), (7.9, "if")], 6.6)
        clip_below(p, 0.0)
    return parts


def capsule(m):
    blue = {key: mat(m, key, idx, 0.45, rough) for key, idx, rough in
            (("b5", 0x35, 0.38), ("b6", 0x36, 0.36), ("b8", 0x38, 0.32), ("ba", 0x3a, 0.3), ("bc", 0x3c, 0.28))}
    glass = mat(m, "cap_glass", 0x3b, 0.25, 0.04, 0.0, 0.45)
    core = mat(m, "cap_core", 0x36, 0.2, 0.4, 0.12)
    glint = mat(m, "cap_glint", 0x8f, 0.0, 0.1, 0.5)
    green = mat(m, "cap_light", 0x28, 0.0, 0.15, 0.5)
    green_hot = mat(m, "cap_light_hot", 0x2c, 0.0, 0.1, 0.6)
    fx, fy = CAPSULE["foot"]
    r, h = CAPSULE["r"], CAPSULE["h"]
    parts = []
    base = mk.prism("cap_base", hexagon(fx, fy, r, 0.0), -0.3, 2.6, blue["b6"])
    mk.bevel(base, 0.35, 2, 40)
    lid = mk.prism("cap_lid", hexagon(fx, fy, r, 0.0), h - 5.2, h, blue["b8"])
    mk.bevel(lid, 0.45, 2, 40)
    plate = mk.prism("cap_plate", hexagon(fx, fy, r - 2.0, 0.0), h - 0.2, h + 0.55, blue["ba"])
    mk.bevel(plate, 0.2, 1, 40)
    for p in (base, lid, plate):
        k.smooth(p, 35)
        paint_light(p, blue, [(-99, "b5"), (5.4, "b6"), (6.3, "b8"), (7.0, "ba"), (7.6, "bc")], 6.6)
        parts.append(p)
    # the glass: an open six-sided tube between them, a dark core inside it, rods up its left and right corners
    hexa = hexagon(fx, fy, r - 0.6, 0.0)
    verts = [Vector((x, y, z)) for z in (2.4, h - 5.0) for x, y in hexa]
    faces = [(i, (i + 1) % 6, 6 + (i + 1) % 6, 6 + i) for i in range(6)]
    glass_obj = k.mesh_object("cap_glass", verts, faces, glass)
    k.recalc_normals(glass_obj)
    parts.append(glass_obj)
    cr = mk.prism("cap_core", hexagon(fx, fy, r - 3.4, 30.0), 2.4, h - 5.0, core)
    parts.append(k.smooth(cr, 30))
    for sx in (-1, 1):
        rod = lathe_z(f"cap_rod{sx:+d}", [(0.7, 2.0), (0.7, h - 4.8)], (fx + sx * (r - 0.2), fy), blue["b8"], 10)
        k.smooth(rod, 50)
        paint_light(rod, blue, [(-99, "b6"), (6.0, "b8"), (7.0, "bc")], 6.6)
        parts.append(rod)
    # glints on the glass towards the camera: thin slanted strips on its front faces
    for i, (gx, gz, gl) in enumerate(((-3.8, 0.3, 3.6), (-1.8, 0.62, 3.0), (1.2, 0.25, 4.2), (3.2, 0.7, 2.4))):
        strip = mk.prism(f"cap_glint{i}", [(-0.28, -0.1), (0.28, -0.1), (0.28, 0.1), (-0.28, 0.1)], -gl / 2, gl / 2, glint)
        strip.data.transform(Matrix.Translation((fx + gx, fy - (r - 0.6) * math.sqrt(3) / 2 - 0.12, 2.4 + gz * (h - 7.4))) @
                             Matrix.Rotation(math.radians(-24), 4, "Y"))
        parts.append(strip)
    # the green light in the middle of the lid's top
    light = mk.ball("cap_light", (fx, fy, h + 0.45), (1.7, 1.7, 1.0), green, segments=20, rings=8, angle=80)
    mk.paint(light, lambda c, n: green_hot if n.z > 0.75 and c.x < fx + 0.5 and c.y > fy - 0.5 else None)
    parts.append(light)
    return parts


# --- Build, checks, export ------------------------------------------------------------------------------------------------
# name: (sprite(s), kind); single sprites: (sprite, builder); two-sprite objects: their pieces' names, sprites, boxes.
SINGLES = [
    ("fruit_pillar_r", 205, lambda m: pillar(m, 1), ("oblique", PILLAR_RISE / PILLAR_H)),
    ("fruit_pillar_l", 243, lambda m: pillar(m, -1), ("oblique", PILLAR_RISE / PILLAR_H)),
    ("fruit_hex_eye", 233, lambda m: hex_eye(m, 233), None),
    ("fruit_hex_eye_235", 235, lambda m: hex_eye(m, 235), None),
    ("fruit_hex_eye_237", 237, lambda m: hex_eye(m, 237), None),
    ("fruit_glyph_tree", 269, lambda m: glyph(m, TREE, TREE_DOTS, 269), None),
    ("fruit_glyph_tree_267", 267, lambda m: glyph(m, TREE, TREE_DOTS, 267), None),
    ("fruit_glyph_tree_153", 153, lambda m: glyph(m, TREE, TREE_DOTS, 153), None),
    ("fruit_glyph_hook", 275, lambda m: glyph(m, HOOK, [], 275), None),
    ("fruit_glyph_hook_273", 273, lambda m: glyph(m, HOOK, [], 273), None),
    ("fruit_glyph_hook_271", 271, lambda m: glyph(m, HOOK, [], 271), None),
]
WHOLES = [
    ("fruit_geoball", geoball, None, (48, 56), [("fruit_geoball_tl", 191, (-30.0, 0.0, 0.0, 34.0), (-12.0, 14.0)),
                                                ("fruit_geoball_tr", 193, (0.0, 30.0, 0.0, 34.0), (12.0, 14.0)),
                                                ("fruit_geoball_bl", 229, (-30.0, 0.0, -34.0, 0.0), (-12.0, -14.0)),
                                                ("fruit_geoball_br", 231, (0.0, 30.0, -34.0, 0.0), (12.0, -14.0))]),
    ("fruit_crystal", crystal, CRYSTAL["rise"] / CRYSTAL["h"], (24, 56),
     [("fruit_crystal_t", 201, (-14.0, 14.0, 0.0, 40.0), (0.0, 14.0)),
      ("fruit_crystal_b", 239, (-14.0, 14.0, -34.0, 0.0), (0.0, -14.0))]),
    ("fruit_capsule", capsule, CAPSULE["rise"] / CAPSULE["h"], (24, 56),
     [("fruit_capsule_t", 169, (-14.0, 14.0, 0.0, 40.0), (0.0, 14.0)),
      ("fruit_capsule_b", 207, (-14.0, 14.0, -34.0, 0.0), (0.0, -14.0))]),
]
SOCKET_RAMP = 3                   # the map's socket (ramp 3's blues) painted into the sprites: not the models' pixels


def object_mask(sheet, sprite, keep_socket=False):
    """The sprite's pixels the model stands for (the socket's blues left out, but where they are the object's own)."""
    from sprite_profile import sprite_indices
    rows = sprite_indices(sheet, sprite, True)
    return [[v is not None and (keep_socket or v >> 4 != SOCKET_RAMP) for v in row] for row in rows]


def finish(parts):
    for obj in parts:
        mk.apply(obj)
    triangulate(parts)
    bpy.context.view_layer.update()


def build():
    options = k.args()
    out = mk.outdir(options)
    only = set(options["only"].split(",")) if "only" in options else None
    sheet = None
    if "check" in options:
        sheets = options["check"]
        sheet = os.path.join(sheets, "enemy_x25.png") if os.path.isdir(sheets) else sheets
    for name, sprite, make, kind in SINGLES:
        if only is not None and name not in only:
            continue
        k.reset()
        m = {}
        parts = make(m)
        finish(parts)
        if kind is not None:
            oblique(parts, kind[1])
        if sheet:
            # the ball, the pillars: their own pixels; the glyphs and the eye: their pixels in the socket (not ramp 3)
            mask = object_mask(sheet, sprite, keep_socket=False)
            seen = [o for o in parts if not any(s.surface_render_method == "BLENDED" for s in o.data.materials)]
            for o in parts:
                o.hide_render = o not in seen
            mk.compare("%s (x25 %d), as the camera sees it" % (name, sprite), mk.coverage(seen, 24, 28), mask)
            for o in parts:
                o.hide_render = False
        shear_to_camera(parts)
        bpy.context.view_layer.update()
        triangulate(parts)
        obj = join(parts, name)
        obj.data.name = name
        bpy.context.scene.view_settings.view_transform = "Standard"
        mk.report(name, [obj], os.path.join(out, name + ".glb"))
        if "preview" in options:
            mk.preview(options["preview"] + name, [obj], size=(24, 28), scale=16, distance=0.6)
    for whole_name, make, K, (w, h), pieces in WHOLES:
        if only is not None and not any(p[0] in only for p in pieces):
            continue
        k.reset()
        m = {}
        whole = make(m)
        finish(whole)
        if K is not None:
            oblique(whole, K)
        bpy.context.view_layer.update()
        mask = None
        if sheet:
            mask = [[False] * w for _ in range(h)]
            for pname, sprite, box, origin in pieces:
                c0 = int(round(origin[0] - 12 + w / 2))
                r0 = int(round(h / 2 - origin[1] - 14))
                for r, line in enumerate(object_mask(sheet, sprite, keep_socket=(whole_name in ("fruit_geoball", "fruit_capsule")))):
                    for c, v in enumerate(line):
                        if v:
                            mask[r0 + r][c0 + c] = True
            mk.compare("%s whole, as the camera sees it" % whole_name, mk.coverage(whole, w, h), mask)
        if "preview" in options:
            seen = []
            for o in whole:
                c = o.copy()
                c.data = o.data.copy()
                bpy.context.scene.collection.objects.link(c)
                seen.append(c)
            if K is not None:
                shear_to_camera(seen)
            for o in whole:
                o.hide_render = True
            bpy.context.scene.view_settings.view_transform = "Standard"
            mk.preview(options["preview"] + whole_name, seen, size=(w, h), scale=12, distance=1.0)
            for o in seen:
                mesh = o.data
                bpy.data.objects.remove(o)
                bpy.data.meshes.remove(mesh)
            for o in whole:
                o.hide_render = False
        for pname, sprite, box, origin in pieces:
            if only is not None and pname not in only:
                continue
            caps = {o.name: o.data.materials[0] for o in whole}
            parts = [p for p in (cut(src, box, caps[src.name]) for src in whole) if p is not None]
            drop_unused(parts)
            for src in whole:
                src.hide_render = True
            if sheet:
                pm = object_mask(sheet, sprite, keep_socket=(whole_name in ("fruit_geoball", "fruit_capsule")))
                seen = [o for o in parts if not any(s.surface_render_method == "BLENDED" for s in o.data.materials)]
                for o in parts:
                    o.hide_render = o not in seen
                mk.compare("%s (x25 %d), as the camera sees it" % (pname, sprite), mk.coverage(seen, 24, 28, centre=origin),
                           pm)
                for o in parts:
                    o.hide_render = False
            if K is not None:
                shear_to_camera(parts)
            mk.transform(parts, Matrix.Translation((-origin[0], -origin[1], 0)))
            bpy.context.view_layer.update()
            triangulate(parts)
            obj = join(parts, pname)
            obj.data.name = pname
            mk.report(pname, [obj], os.path.join(out, pname + ".glb"))
            bpy.data.objects.remove(obj)
            for src in whole:
                src.hide_render = False


if __name__ == "__main__":
    build()
