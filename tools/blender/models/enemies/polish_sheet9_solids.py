"""Helpers of round 38's rebuilt sheet 9 machines (polish_eye_spheres.py, polish_eyespy_boss.py,
polish_time_capsule.py), which replace round 36's heightfields painted from the sprites' pixels
(polish_sheet9_kit.py) with solids. Not a model script itself.

Every object is built whole in its picture's plane (x, y where the sprites draw it, z up towards the camera) from
separate solids: armour plates (shell_plate: lying on a surface over a smooth outline, a quarter-round bevel offset from
the outline, straight walls, a sparse Delaunay top, normals the surface's), turned parts along any axis (lathe_between),
lofts along paths (tube_along), rings round a closed path (loop_loft), rivets and domes standing on a surface along its
normal (dome_on). Each solid takes one palette material by its part (painted or bare metal, glass, lamp, rubber); the
shading is the geometry's under the game's light. Then the whole is cut into its pieces along the sprites' edges
(polish_coral_manta.cut, the cuts capped in the inside's colour), each piece sheared along the game camera's line of
sight (y - z tan 20: the camera sees every point where the sprite draws it; polish_fleet_walker.shear_to_camera), moved
to its origin, triangulated, joined and exported (export_pieces).

flatten(): an object built with more height than its layer leaves it (a ball as round as the sprite paints it) is
squashed in z keeping its built normals, so that it is shaded as the rounder solid (the game's camera looks nearly
straight down: what it sees of a solid's height is its shading).

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera. A picture whose top
left corner is (left, top) has its column c's left edge at x = left + c and its row r's top edge at y = top - r.
"""
import math
import os
import sys

import bpy
import numpy as np
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
import polish_machine_kit as mk  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402
from polish_deli_boss import join, drop_unused  # noqa: E402
from polish_coral_manta import cut  # noqa: E402
from polish_fleet_walker import shear_to_camera, merge_materials, remove  # noqa: E402,F401

TAN_T = math.tan(math.radians(20.0))
MAX_MATERIALS = 15


# --- Materials ------------------------------------------------------------------------------------------------------

def pal(name, index, metallic=0.3, roughness=0.4, glow=0.0):
    """A palette material (named <name>@<index>), glowing `glow` in its own colour."""
    extra = dict(emission=k.level_palette()[index], emission_strength=glow) if glow > 0 else {}
    return k.material(name, palette=index, metallic=metallic, roughness=roughness, **extra)


# --- Outlines -------------------------------------------------------------------------------------------------------

def chaikin_open(points, iterations=2):
    """Rounds an open polyline's corners, its ends kept."""
    pts = [tuple(p) for p in points]
    for _ in range(iterations):
        if len(pts) < 3:
            return pts
        out = [pts[0]]
        for i in range(len(pts) - 1):
            p, q = pts[i], pts[i + 1]
            if i > 0:
                out.append(tuple(0.75 * a + 0.25 * b for a, b in zip(p, q)))
            if i < len(pts) - 2:
                out.append(tuple(0.25 * a + 0.75 * b for a, b in zip(p, q)))
        out.append(pts[-1])
        pts = out
    return pts


def signed_area(poly):
    return 0.5 * sum(poly[i][0] * poly[(i + 1) % len(poly)][1] - poly[(i + 1) % len(poly)][0] * poly[i][1]
                     for i in range(len(poly)))


def dedupe(poly, eps=1e-4):
    out = []
    for p in poly:
        if not out or math.dist(p, out[-1]) > eps:
            out.append(tuple(p))
    if len(out) > 2 and math.dist(out[0], out[-1]) <= eps:
        out.pop()
    return out


def inset(poly, g, limit=2.5):
    """A closed polygon moved g inwards (each corner along its bisector, mitred at most limit * g)."""
    poly = dedupe(poly)
    n = len(poly)
    s = 1.0 if signed_area(poly) > 0 else -1.0     # counter-clockwise: inwards is to the left of each edge
    out = []
    for i in range(n):
        p0, p1, p2 = Vector(poly[i - 1]), Vector(poly[i]), Vector(poly[(i + 1) % n])
        e1, e2 = (p1 - p0), (p2 - p1)
        if e1.length < 1e-9 or e2.length < 1e-9:
            continue
        e1.normalize()
        e2.normalize()
        n1 = Vector((-e1.y, e1.x)) * s
        n2 = Vector((-e2.y, e2.x)) * s
        b = n1 + n2
        if b.length < 1e-6:
            b = n1
        b.normalize()
        d = g / max(b.dot(n1), 1.0 / limit)
        out.append(tuple(p1 + b * d))
    return out


def ellipse_arc(centre, radii, a0, a1, step=0.5):
    """Points on an ellipse (x, y) from angle a0 to a1 (degrees, counter-clockwise from +x; a1 < a0 runs clockwise),
    about `step` apart."""
    (cx, cy), (rx, ry) = centre, radii
    length = abs(math.radians(a1 - a0)) * 0.5 * (rx + ry)
    n = max(2, int(math.ceil(length / step)))
    return [(cx + rx * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
             cy + ry * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]


def angle_on(centre, radii, p):
    """The angle (degrees) of a point seen from an ellipse's middle, in the ellipse's own parameter."""
    (cx, cy), (rx, ry) = centre, radii
    return math.degrees(math.atan2((p[1] - cy) / ry, (p[0] - cx) / rx))


def on_ellipse(centre, radii, p):
    """The point of the ellipse at p's angle."""
    a = math.radians(angle_on(centre, radii, p))
    return (centre[0] + radii[0] * math.cos(a), centre[1] + radii[1] * math.sin(a))


# --- Solids ---------------------------------------------------------------------------------------------------------

def resample_closed(poly, spacing):
    """A closed polygon resampled by arc length to points about `spacing` apart."""
    poly = dedupe(poly)
    n = len(poly)
    lengths = [math.dist(poly[i], poly[(i + 1) % n]) for i in range(n)]
    total = sum(lengths)
    count = max(8, int(round(total / spacing)))
    out, i, walked = [], 0, 0.0
    for c in range(count):
        target = total * c / count
        while walked + lengths[i] < target:
            walked += lengths[i]
            i += 1
        t = (target - walked) / lengths[i] if lengths[i] > 0 else 0.0
        (x0, y0), (x1, y1) = poly[i], poly[(i + 1) % n]
        out.append((x0 + (x1 - x0) * t, y0 + (y1 - y0) * t))
    return out


def _dense(poly, step):
    """A closed polygon with its long edges split (`step` apart at most), its points kept."""
    poly = dedupe(poly)
    n = len(poly)
    out = []
    for i in range(n):
        a, b = Vector(poly[i]), Vector(poly[(i + 1) % n])
        m = max(1, int(math.ceil((b - a).length / step)))
        for j in range(m):
            out.append(tuple(a + (b - a) * (j / m)))
    return out


def _inside(loops, pts):
    """Even-odd inside test of points in loops."""
    a, b = [], []
    for loop in loops:
        for i in range(len(loop)):
            a.append(loop[i])
            b.append(loop[(i + 1) % len(loop)])
    a, b = np.array(a, float), np.array(b, float)
    pts = np.asarray(pts, float)
    px_, py_ = pts[:, :1], pts[:, 1:2]
    ax, ay, bx, by = a[:, 0][None], a[:, 1][None], b[:, 0][None], b[:, 1][None]
    straddle = (ay > py_) != (by > py_)
    with np.errstate(divide="ignore", invalid="ignore"):
        cross_x = ax + (py_ - ay) * (bx - ax) / np.where(by - ay == 0, 1e-12, by - ay)
    return (straddle & (px_ < cross_x)).sum(1) % 2 == 1


def _distance(loops, pts):
    a, b = [], []
    for loop in loops:
        for i in range(len(loop)):
            a.append(loop[i])
            b.append(loop[(i + 1) % len(loop)])
    a, b = np.array(a, float), np.array(b, float)
    pts = np.asarray(pts, float)
    d = b - a
    l2 = np.maximum((d * d).sum(1), 1e-12)
    rel = pts[:, None, :] - a[None]
    t = np.clip((rel * d[None]).sum(2) / l2[None], 0.0, 1.0)
    near = a[None] + t[:, :, None] * d[None]
    return np.sqrt(((pts[:, None, :] - near) ** 2).sum(2)).min(1)


def round_corners(poly, sigma, step=0.25):
    """A closed polygon's corners rounded over about sigma (resampled `step` apart, averaged along itself)."""
    pts = resample_closed(_dense(poly, step), step)
    n = len(pts)
    r = int(math.ceil(2.5 * sigma / step))
    w = [math.exp(-0.5 * (i * step / sigma) ** 2) for i in range(-r, r + 1)]
    tot = sum(w)
    out = []
    for i in range(n):
        x = sum(w[j + r] * pts[(i + j) % n][0] for j in range(-r, r + 1)) / tot
        y = sum(w[j + r] * pts[(i + j) % n][1] for j in range(-r, r + 1)) / tot
        out.append((x, y))
    return out


BEVEL_STEPS = (0.0, 30.0, 60.0, 90.0)     # the bevel's rings: degrees round its quarter circle from the wall


def shell_plate(name, outer, holes, base, base_normal, thick, bevel, mat, side_mat=None, edge=0.55, inner=1.0,
                drop=1.2, steps=BEVEL_STEPS):
    """An armour plate lying on a surface (base(x, y) its height, base_normal(x, y) its normal): over the outline
    `outer` with `holes` (closed polygons), its top `thick` over the surface, its edges a quarter round of `bevel`
    (rings offset from the outline, so the rounding is a clean band), straight walls down to `drop` under the surface
    and an underside. Its normals are the surface's and the rounding's (custom normals: smooth whatever the
    triangulation; the top a sparse Delaunay fill, `inner` apart)."""
    from mathutils import geometry
    loops = [(outer, 1.0)] + [(h, -1.0) for h in holes]
    verts, normals_of = [], []          # per vertex: position; per face corner normal comes from kind
    faces, kinds, corner_n = [], [], []
    rings_all = []
    for poly, sense in loops:
        ring0 = resample_closed(poly, edge)
        if (signed_area(ring0) > 0) != (sense > 0):
            ring0 = ring0[::-1]
        rings = []
        for psi in steps:
            f = 1.0 - math.cos(math.radians(psi))
            # (into the plate: inwards of the outline, outwards of a hole, which runs clockwise)
            pts = inset(ring0, sense * bevel * f) if f > 1e-9 else [tuple(p) for p in ring0]
            rings.append((psi, pts))
        rings_all.append(rings)
    # the outward direction at each point of a ring (away from the plate's inside)
    def outward(pts, i):
        p0, p2 = Vector(pts[i - 1]), Vector(pts[(i + 1) % len(pts)])
        t = (p2 - p0)
        if t.length < 1e-9:
            return Vector((1.0, 0.0))
        t.normalize()
        return Vector((t.y, -t.x))          # rings run counter-clockwise round the plate's inside: right is out

    def tangent_out(x, y, o2):
        nb = Vector(base_normal(x, y))
        o = Vector((o2.x, o2.y, 0.0))
        o = o - nb * o.dot(nb)
        return o.normalized() if o.length > 1e-9 else Vector((o2.x, o2.y, 0.0)).normalized(), nb

    vid = {}
    ring_ids = []
    for li, rings in enumerate(rings_all):
        ids_l = []
        for ri, (psi, pts) in enumerate(rings):
            ids = []
            for i, (x, y) in enumerate(pts):
                z = base(x, y) + thick - bevel * (1.0 - math.sin(math.radians(psi)))
                ids.append(len(verts))
                verts.append(Vector((x, y, z)))
                o2 = outward(rings[0][1], i)
                ot, nb = tangent_out(x, y, o2)
                normals_of.append((ot * math.cos(math.radians(psi)) + nb * math.sin(math.radians(psi))).normalized())
            ids_l.append(ids)
        # the wall's foot
        foot = []
        for i, (x, y) in enumerate(rings[0][1]):
            foot.append(len(verts))
            verts.append(Vector((x, y, max(0.02, base(x, y) - drop))))
            o2 = outward(rings[0][1], i)
            ot, nb = tangent_out(x, y, o2)
            normals_of.append(ot)
        ring_ids.append((ids_l, foot))
    # bevel strips and walls
    for ids_l, foot in ring_ids:
        n = len(foot)
        for r in range(len(ids_l) - 1):
            a_, b_ = ids_l[r], ids_l[r + 1]
            for i in range(n):
                j = (i + 1) % n
                faces.append((a_[i], a_[j], b_[j], b_[i]))
                kinds.append("bevel")
        top0 = ids_l[0]
        for i in range(n):
            j = (i + 1) % n
            faces.append((foot[i], foot[j], top0[j], top0[i]))
            kinds.append("wall")
    # the top: the innermost rings filled (constrained Delaunay), with points `inner` apart inside them
    inner_loops = [[tuple(verts[v].xy) for v in ids_l[-1]] for ids_l, _ in ring_ids]
    xs = [p[0] for lp in inner_loops for p in lp]
    ys = [p[1] for lp in inner_loops for p in lp]
    grid = []
    rs = inner * math.sqrt(3) / 2
    for jy in range(int((max(ys) - min(ys)) / rs) + 2):
        y = min(ys) + jy * rs
        for ix in range(int((max(xs) - min(xs)) / inner) + 2):
            grid.append((min(xs) + (inner / 2 if jy % 2 else 0.0) + ix * inner, y))
    if grid:
        grid = np.array(grid)
        keep = _inside(inner_loops, grid)
        grid = grid[keep]
        if len(grid):
            grid = grid[_distance(inner_loops, grid) > 0.55 * inner]
    loop_pts, edges = [], []
    owner = []
    for (ids_l, _), lp in zip(ring_ids, inner_loops):
        start = len(loop_pts)
        for v in ids_l[-1]:
            loop_pts.append(tuple(verts[v].xy))
            owner.append(v)
        m = len(ids_l[-1])
        edges += [(start + i, start + (i + 1) % m) for i in range(m)]
    pts2 = [Vector(p) for p in loop_pts] + [Vector(tuple(p)) for p in grid]
    out_v, _oe, out_f, orig_v, *_ = geometry.delaunay_2d_cdt(pts2, edges, [], 0, 1e-6)
    index = {}
    for k_, ov in enumerate(orig_v):
        if ov and ov[0] < len(owner):
            index[k_] = owner[ov[0]]
        else:
            x, y = out_v[k_].x, out_v[k_].y
            index[k_] = len(verts)
            verts.append(Vector((x, y, base(x, y) + thick)))
            normals_of.append(Vector(base_normal(x, y)).normalized())
    tris = [f for f in out_f if len(f) == 3]
    if tris:
        cents = np.array([[sum(out_v[i].x for i in f) / 3, sum(out_v[i].y for i in f) / 3] for f in tris])
        for f, ok in zip(tris, _inside(inner_loops, cents)):
            if ok:
                faces.append(tuple(index[i] for i in f))
                kinds.append("top")
    # the underside: the walls' feet filled
    foot_loops = [[tuple(verts[v].xy) for v in foot] for _, foot in ring_ids]
    fpts, fedges, fowner = [], [], []
    for (_, foot) in ring_ids:
        start = len(fpts)
        for v in foot:
            fpts.append(Vector(verts[v].xy))
            fowner.append(v)
        m = len(foot)
        fedges += [(start + i, start + (i + 1) % m) for i in range(m)]
    uv, _ue, uf, uo, *_ = geometry.delaunay_2d_cdt(fpts, fedges, [], 0, 1e-6)
    utris = [f for f in uf if len(f) == 3 and all(uo[i] and uo[i][0] < len(fowner) for i in f)]
    if utris:
        cents = np.array([[sum(uv[i].x for i in f) / 3, sum(uv[i].y for i in f) / 3] for f in utris])
        for f, ok in zip(utris, _inside(foot_loops, cents)):
            if ok:
                faces.append(tuple(fowner[uo[i][0]] for i in reversed(f)))
                kinds.append("under")
    obj = k.mesh_object(name, [tuple(v) for v in verts], faces)
    mesh = obj.data
    top_mat, side = mat, side_mat or mat
    mesh.materials.append(top_mat)
    if side is not top_mat:
        mesh.materials.append(side)
    k.recalc_normals(obj)
    # recalc may flip faces: the corners' normals by the faces' kinds, the underside facing down
    mesh.polygons.foreach_set("material_index", [0 if kd in ("top", "bevel") or side is top_mat else 1
                                                 for kd in kinds])
    mesh.polygons.foreach_set("use_smooth", [True] * len(mesh.polygons))
    cn = []
    for poly, kd in zip(mesh.polygons, kinds):
        for li in poly.loop_indices:
            vi = mesh.loops[li].vertex_index
            if kd == "under":
                cn.append(tuple(-Vector(base_normal(*verts[vi].xy)).normalized()))
            else:
                cn.append(tuple(normals_of[vi]))
    mesh.normals_split_custom_set(cn)
    mesh.update()
    return obj


def frame_of(n):
    """Two unit vectors across the direction n (a right-handed frame u, v, n), the same every run."""
    n = Vector(n).normalized()
    ref = Vector((0.0, 0.0, 1.0)) if abs(n.z) < 0.9 else Vector((1.0, 0.0, 0.0))
    u = ref.cross(n).normalized()
    v = n.cross(u).normalized()
    return u, v


def lathe_between(name, profile, p0, p1, mat, around=24, smooth=50.0, roll=None):
    """A turned part along the line from p0 towards p1: profile [(t, radius), ...] with t the distance from p0 along
    it (increasing), its ends closed on the axis. roll: a vector its sections' first point leans towards."""
    a = (Vector(p1) - Vector(p0)).normalized()
    u, v = frame_of(a)
    if roll is not None:
        r = Vector(roll) - a * Vector(roll).dot(a)
        if r.length > 1e-6:
            u = r.normalized()
            v = a.cross(u).normalized()
    o = Vector(p0)
    rings = []
    for t, r in profile:
        c = o + a * t
        rings.append([c + (u * math.cos(2 * math.pi * j / around) + v * math.sin(2 * math.pi * j / around)) *
                      max(r, 1e-3) for j in range(around)])
    obj = k.loft(name, rings, mat, start_point=o + a * profile[0][0], end_point=o + a * profile[-1][0])
    return k.smooth(obj, smooth)


def tube_along(name, points, radii, mat, around=16, smooth=60.0, cap=True, squash=1.0, up=(0.0, 0.0, 1.0)):
    """A round part along a path of (x, y, z) points (radii: one per point), its sections squashed towards `up`."""
    pts = [Vector(p) for p in points]
    upv = Vector(up)
    rings = []
    for i, p in enumerate(pts):
        d = (pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]).normalized()
        side = d.cross(upv)
        if side.length < 1e-6:
            side = Vector((1.0, 0.0, 0.0))
        side.normalize()
        w = side.cross(d).normalized()
        r = radii[i]
        rings.append([p + side * (r * math.cos(2 * math.pi * j / around)) +
                      w * (r * squash * math.sin(2 * math.pi * j / around)) for j in range(around)])
    d0 = (pts[1] - pts[0]).normalized()
    d1 = (pts[-1] - pts[-2]).normalized()
    obj = k.loft(name, rings, mat, cap_start=cap, cap_end=cap, start_point=pts[0] - d0 * radii[0] * 0.5,
                 end_point=pts[-1] + d1 * radii[-1] * 0.5)
    return k.smooth(obj, smooth)


def loop_loft(name, sections, mat, smooth=50.0):
    """A closed ring through cross-sections (closed polygons of equal point counts) round a closed path."""
    n = len(sections[0])
    m = len(sections)
    verts = [tuple(p) for s in sections for p in s]
    faces = []
    for i in range(m):
        i2 = (i + 1) % m
        for j in range(n):
            j2 = (j + 1) % n
            faces.append((i * n + j, i * n + j2, i2 * n + j2, i2 * n + j))
    obj = k.mesh_object(name, verts, faces, mat)
    k.recalc_normals(obj)
    return k.smooth(obj, smooth)


def turned_on(name, point, normal, profile, mat, segments=16, smooth=45.0, squash=(1.0, 1.0)):
    """A turned part (profile [(radius, z), ...] from its foot up, z 0 on the surface; its plan squashed in x, y)
    standing on a surface at point along its normal: a machined boss, a bolt head, a lamp's lens."""
    obj = mk.lathe(name, profile, (0.0, 0.0), mat, segments=segments, squash=squash)
    rot = Vector((0.0, 0.0, 1.0)).rotation_difference(Vector(normal).normalized()).to_matrix().to_4x4()
    obj.data.transform(Matrix.Translation(Vector(point)) @ rot)
    k.recalc_normals(obj)
    return k.smooth(obj, smooth)


def dome_on(name, point, normal, radius, height, mat, segments=12, steps=4, sink=0.6, smooth=70.0):
    """A small dome (a rivet, a bolt head, a boss) standing on a surface at point along its normal, its foot sunk
    `sink` into it."""
    obj = mk.dome(name, (0.0, 0.0), (radius, radius, height + sink), -sink, mat, segments=segments, steps=steps)
    rot = Vector((0.0, 0.0, 1.0)).rotation_difference(Vector(normal).normalized()).to_matrix().to_4x4()
    obj.data.transform(Matrix.Translation(Vector(point)) @ rot)
    return k.smooth(obj, smooth)


# --- Normals, the camera --------------------------------------------------------------------------------------------

def corner_normals(obj):
    return [Vector(cn.vector) for cn in obj.data.corner_normals]


def flatten(objects, s, keep=1.0, rounder=1.0):
    """Squashes the objects in z by s, keeping their normals as built (keep 1) or as the squash turns them (keep 0)
    or between; rounder > 1 turns the kept normals as if the solid were that much taller still."""
    for obj in objects:
        mesh = obj.data
        built = corner_normals(obj)
        for v in mesh.vertices:
            v.co.z *= s
        out = []
        for n in built:
            squashed = Vector((n.x, n.y, n.z / s)).normalized()
            kept = Vector((n.x, n.y, n.z / rounder)).normalized()
            m = (kept * keep + squashed * (1.0 - keep))
            out.append(tuple(m.normalized() if m.length > 1e-9 else squashed))
        mesh.normals_split_custom_set(out)
        mesh.update()


def mirror_copy(obj, axis_x, name):
    """A copy of the object mirrored about the line x = axis_x, its faces' winding and its normals mirrored with it."""
    c = obj.copy()
    c.data = obj.data.copy()
    c.name = name
    bpy.context.scene.collection.objects.link(c)
    mesh = c.data
    corner = {}
    for poly in mesh.polygons:
        for li in poly.loop_indices:
            n = mesh.corner_normals[li].vector
            corner[(poly.index, mesh.loops[li].vertex_index)] = (-n.x, n.y, n.z)
    mesh.transform(Matrix.Translation((2 * axis_x, 0, 0)) @ Matrix.Scale(-1, 4, (1, 0, 0)))
    mesh.flip_normals()
    normals = [None] * len(mesh.loops)
    for poly in mesh.polygons:
        for li in poly.loop_indices:
            normals[li] = corner[(poly.index, mesh.loops[li].vertex_index)]
    mesh.normals_split_custom_set(normals)
    mesh.update()
    return c


def flat(z):
    return (lambda x, y: z), (lambda x, y: (0.0, 0.0, 1.0))


# --- Pieces ---------------------------------------------------------------------------------------------------------

def export_pieces(whole, pieces, cap_mat, options, sheet=None, label="9"):
    """Cuts the whole (in the picture's plane) into its pieces, checks each against its sprite as the camera sees it,
    shears it for the camera, moves it to its origin, triangulates, joins and exports it. pieces: (name, sprite, box
    (x0, x1, y0, y1), origin (x, y), rows (r0, r1) of the sprite to compare or None)."""
    out = mk.outdir(options)
    only = set(options["only"].split(",")) if "only" in options else None
    scores = {}
    bpy.context.view_layer.update()        # (the solids' bounding boxes are stale after moving their vertices)
    for name, sprite, box, origin, rows in pieces:
        if only is not None and name not in only:
            continue
        parts = [p for p in (cut(src, box, cap_mat) for src in whole) if p is not None]
        drop_unused(parts)
        for src in whole:
            src.hide_render = True
        if sheet and sprite is not None:
            covered = mk.coverage(parts, 24, 28, centre=origin)
            mask = k.sprite_mask(sheet, sprite)
            if rows is not None:
                for r in range(28):
                    if not rows[0] <= r < rows[1]:
                        covered[r] = [False] * 24
                        mask[r] = [False] * 24
            scores[name] = mk.compare("%s (%s %d%s), as the camera sees it" % (
                name, label, sprite, "" if rows is None else ", rows %d-%d" % (rows[0], rows[1] - 1)), covered, mask)
        shear_to_camera(parts)
        mk.transform(parts, Matrix.Translation((-origin[0], -origin[1], 0.0)))
        bpy.context.view_layer.update()
        triangulate(parts)
        if "stats" in options:
            for o in sorted(parts, key=lambda o: -mk.triangles([o]))[:10]:
                print("    %-26s %6d" % (o.name, mk.triangles([o])))
        obj = join(parts, name) if len(parts) > 1 else parts[0]
        obj.name = name
        obj.data.name = name
        drop_unused([obj])
        merge_materials(obj, MAX_MATERIALS)
        bpy.context.scene.view_settings.view_transform = "Standard"
        mk.report(name, [obj], os.path.join(out, name + ".glb"))
        if "preview" in options and options.get("pieces") == "1":
            mk.preview(options["preview"] + name, [obj])
        remove([obj])
        for src in whole:
            src.hide_render = False
    return scores


def whole_preview(prefix, objects, size, centre=(0.0, 0.0)):
    """Top and three-quarter views of a whole (in the picture's plane, sheared for the camera on copies)."""
    copies = []
    for o in objects:
        c = o.copy()
        c.data = o.data.copy()
        bpy.context.scene.collection.objects.link(c)
        copies.append(c)
    for o in objects:
        o.hide_render = True
    shear_to_camera(copies)
    mk.preview(prefix, copies, size=size, centre=centre, distance=max(size) / 44.0)
    remove(copies)
    for o in objects:
        o.hide_render = False
