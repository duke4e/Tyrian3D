"""Helpers for the batch AE models of wave 3 (sheet ', FRUIT and CORAL; written x27 in models.cfg): the sprites'
pixels (wave3_ae_art.py), and the frames, painting, parts and build loop of batch AA (wave3_aa_kit: pixel frames,
reliefs inflated from pixel regions, painting faces by the sprite's pixel under them, stand-alone models and whole
objects cut into their sprites' pieces, the silhouette check), with batch Y's limbs, rings and cones
(wave3_y_kit), and a few parts of their own: thin plates inflated from pixel regions, bumpy peel, tapering
limbs along curves, glowing fruit slices.

Coordinates as in tyrkit: 1 unit = 1 game pixel, X right, Y up the screen, Z up (towards the camera);
the origin is the sprite's centre (or the whole object's, for objects the game draws in pieces).
Pixel (column c, row r) of an art with origin (ox, oy) covers x = c - ox .. c + 1 - ox,
y = oy - r - 1 .. oy - r.
"""
import math
import os
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector, noise

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402,F401
import wave1_d_shapes as sh  # noqa: E402,F401
import wave3_j_kit as w  # noqa: E402,F401
import wave3_n_kit as n  # noqa: E402,F401
import wave3_v_kit as v  # noqa: E402,F401
import wave3_aa_kit as aa  # noqa: E402,F401
import wave3_y_kit as yk  # noqa: E402,F401
import wave3_ae_art as art  # noqa: E402,F401
from wave3_j_kit import (pal, paint_faces, lathe_axis, hoop, tube, catmull, sphere, rounded_box, meshes,  # noqa: E402,F401
                         bake, transform)
from wave3_v_kit import (Frame, Painter, paint_sprite, pixelate, merge_flat, relief, outlines_of,  # noqa: E402,F401
                         mirror_copies, lift, smoothstep)

model = n.model
pieced = n.pieced
run = v.run
PROTECT = v.PROTECT
piece = aa.piece
grid_pieces = aa.grid_pieces
lens = aa.lens
ellipsoid_point = aa.ellipsoid_point
loft_path = yk.loft_path
torus = yk.torus


def frame(name, width, origin):
    """A Frame of one of wave3_ae_art's pixel arts."""
    return Frame(getattr(art, name), width, origin)


# --- Shaping -----------------------------------------------------------------------------------------

def displace_z(obj, fn):
    """Moves every vertex up by fn(x, y, z)."""
    sh.apply_modifiers(obj)
    for vt in obj.data.vertices:
        vt.co.z += fn(vt.co.x, vt.co.y, vt.co.z)
    obj.data.update()
    return obj


def bumps(obj, amount, scale, seed=0.0, centre=None, min_z=None):
    """Displaces the vertices along their direction from `centre` (default: along their normals) by smooth
    noise: dimpled peel, knobbly skin. scale: the bumps' size in pixels."""
    sh.apply_modifiers(obj)
    obj.data.update()
    off = Vector((seed * 13.1, seed * 7.7, seed * 3.3))
    for vt in obj.data.vertices:
        if min_z is not None and vt.co.z < min_z:
            continue
        d = noise.noise(vt.co / scale + off)
        direction = (vt.co - Vector(centre)).normalized() if centre is not None else vt.normal
        vt.co += direction * d * amount
    obj.data.update()
    return obj


def plate(name, polys, mat, height, z, aspect=0.45, rim=0.2, bottom=1.0, spacing=0.4, sigma=1.0, angle=55):
    """A thin part inflated from polygons, centred on height z: its top rises `height` at most over its spine
    (as high as `aspect` times its local half-width), its underside the same below (bottom=1)."""
    obj = sh.inflate(name, polys, mat, sh.round_profile(aspect=aspect, max_height=height), bottom=bottom, base=z,
                     rim=rim, spacing=spacing, sigma=sigma)
    return k.smooth(obj, angle)


def limb(name, points, radii, mat, segments=14, squash=1.0, step=0.5, angle=60):
    """A tapering round limb (horn, pincer, tendril) along a smooth curve through 3D points; radii: one per
    point (interpolated along the curve). squash flattens its cross-section towards +Z."""
    pts = catmull(points, step)
    # The radius along the curve: by arc length between the control points.
    ctrl = [Vector(p) for p in points]
    lengths = [0.0]
    for a, b in zip(ctrl, ctrl[1:]):
        lengths.append(lengths[-1] + (b - a).length)
    total = [0.0]
    for a, b in zip(pts, pts[1:]):
        total.append(total[-1] + (b - a).length)
    scale = lengths[-1] / max(total[-1], 1e-6)
    rs = []
    for t in total:
        s = t * scale
        for i in range(len(lengths) - 1):
            if s <= lengths[i + 1] or i == len(lengths) - 2:
                f = (s - lengths[i]) / max(lengths[i + 1] - lengths[i], 1e-6)
                rs.append(radii[i] + (radii[i + 1] - radii[i]) * min(1.0, max(0.0, f)))
                break
    return loft_path(name, pts, [(r, r * squash) for r in rs], mat, segments=segments, smooth_angle=angle)


def band_y(name, centre, major, minor, mat, segments=32, sides=8, squash=1.0):
    """A ring round an axis along Y (a band round a pod or a pipe lying along the screen) at centre."""
    obj = torus(name, (0.0, 0.0, 0.0), major, minor, mat, segments, sides)
    obj.data.transform(Matrix.Translation(Vector(centre)) @ Matrix.Scale(squash, 4, (0, 0, 1)) @
                       Matrix.Rotation(math.radians(90), 4, "X"))
    k.recalc_normals(obj)
    return obj


def fillet_path(points, radius, step=0.5):
    """A path through 3D points with its corners rounded (arcs of about `radius`), sampled every `step`:
    the axis of a bent pipe."""
    pts = [Vector(p) for p in points]
    out = [pts[0]]
    for i in range(1, len(pts) - 1):
        a, b, c = pts[i - 1], pts[i], pts[i + 1]
        d0, d1 = (b - a).normalized(), (c - b).normalized()
        angle = d0.angle(d1) if (d0 - d1).length > 1e-6 else 0.0
        cut = min(radius * math.tan(angle / 2), (b - a).length * 0.45, (c - b).length * 0.45)
        p0, p1 = b - d0 * cut, b + d1 * cut
        # The straight run to the arc, then the arc (a quadratic curve through the corner).
        seg = p0 - out[-1]
        count = max(1, int(seg.length / step))
        out += [out[-1] + seg * (j / count) for j in range(1, count + 1)]
        count = max(2, int((angle * radius) / step))
        for j in range(1, count + 1):
            t = j / count
            out.append(p0 * (1 - t) ** 2 + b * 2 * t * (1 - t) + p1 * t * t)
    seg = pts[-1] - out[-1]
    count = max(1, int(seg.length / step))
    out += [out[-1] + seg * (j / count) for j in range(1, count + 1)]
    return out


def pipe(name, points, radius, mat, bend=3.5, segments=16, squash=1.0, cap=0.45):
    """A round pipe along straight runs between 3D points, its bends rounded, its ends closed by low rounded
    caps (`cap` times the radius deep)."""
    path = fillet_path(points, bend)
    t0 = (path[1] - path[0]).normalized()
    t1 = (path[-1] - path[-2]).normalized()
    head, tail, sections_head, sections_tail = [], [], [], []
    for f_, d in ((0.93, 0.35), (0.72, 0.75), (0.42, 0.95)):
        head.insert(0, path[0] - t0 * radius * cap * d)
        sections_head.insert(0, (radius * f_, radius * f_ * squash))
        tail.append(path[-1] + t1 * radius * cap * d)
        sections_tail.append((radius * f_, radius * f_ * squash))
    full = head + path + tail
    sections = sections_head + [(radius, radius * squash)] * len(path) + sections_tail
    rings = []
    upv = Vector((0, 0, 1))
    for i, p in enumerate(full):
        a, b = full[max(i - 1, 0)], full[min(i + 1, len(full) - 1)]
        t = (b - a).normalized()
        side = t.cross(upv)
        if side.length < 1e-6:
            side = t.cross(Vector((1, 0, 0)))
        side.normalize()
        u = side.cross(t).normalized()
        hw, hh = sections[i]
        rings.append([p + side * math.cos(2 * math.pi * j / segments) * hw + u * math.sin(2 * math.pi * j / segments) * hh
                      for j in range(segments)])
    obj = k.loft(name, rings, mat, start_point=path[0] - t0 * radius * cap, end_point=path[-1] + t1 * radius * cap)
    return k.smooth(obj, 50)


def disc(name, centre, radius, height, mat, segments=40, bevel=0.35, radius_y=None, dome=0.0):
    """A low round disc standing on centre's z (a lens, a slice): its top edge rounded over `bevel`, its top
    bulging `dome`."""
    cx, cy, cz = centre
    ry = radius_y if radius_y is not None else radius
    rings = []
    profile = [(0.0, 1.0)]
    steps = 4
    for i in range(steps + 1):
        a = math.radians(90 * i / steps)
        profile.append((height - bevel + bevel * math.sin(a), 1.0 - bevel * (1 - math.cos(a)) / radius))
    for j in (0.66, 0.33):
        profile.append((height + dome * (1 - j * j), (1.0 - bevel / radius) * j))
    for z, f in profile:
        rings.append([Vector((cx + radius * f * math.cos(2 * math.pi * i / segments),
                              cy + ry * f * math.sin(2 * math.pi * i / segments), cz + z)) for i in range(segments)])
    obj = k.loft(name, rings, mat, start_point=(cx, cy, cz), end_point=(cx, cy, cz + height + dome))
    return k.smooth(obj, 40)


def lemon_slice(name, cx, cy, z, radius, tilt=0.0, glow=1.0):
    """A lemon slice lying flat at (cx, cy, z) (the lemon beetle's eyes, the pineapple's lamps): yellow rind,
    white pith, eight glowing segments of juice, white spokes between them; tilted `tilt` degrees about y;
    glow scales its light."""
    rind = pal("lemon_rind", 0x7c, metallic=0.05, roughness=0.35)
    pith = pal("lemon_pith", 0x7f, metallic=0.0, roughness=0.5, glow=0.4 * glow)
    juice = pal("lemon_juice", 0x7d, metallic=0.0, roughness=0.12, glow=1.1 * glow)
    juice2 = pal("lemon_juice2", 0x7e, metallic=0.0, roughness=0.12, glow=1.3 * glow)
    parts = [disc(f"{name}_rind", (0.0, 0.0, -1.2), radius, 1.9, rind, 48, bevel=0.6),
             disc(f"{name}_pith", (0.0, 0.0, -0.4), radius - 1.0, 1.35, pith, 48, bevel=0.3)]
    # Eight wedges of juice, domed, white gaps between them.
    for i in range(8):
        a0 = 2 * math.pi * i / 8 + math.radians(4.5)
        a1 = 2 * math.pi * (i + 1) / 8 - math.radians(4.5)
        outline = [(0.55 * math.cos((a0 + a1) / 2), 0.55 * math.sin((a0 + a1) / 2))]
        for j in range(7):
            a = a0 + (a1 - a0) * j / 6
            outline.append(((radius - 1.7) * math.cos(a), (radius - 1.7) * math.sin(a)))
        wedge = sh.inflate(f"{name}_juice{i}", [outline], juice if i % 2 else juice2,
                           sh.pillow_profile(0.5, 0.9, crown=0.25), bottom=0.0, base=0.9, rim=0.05, spacing=0.45)
        k.smooth(wedge, 50)
        parts.append(wedge)
    m = Matrix.Translation((cx, cy, z)) @ Matrix.Rotation(math.radians(tilt), 4, "Y")
    for p in parts:
        p.data.transform(m)
    return parts


def ellipse_ring(centre, rx, ry, z, count=48, angle=0.0):
    """Points round an ellipse at height z."""
    cx, cy = centre
    ca, sa = math.cos(angle), math.sin(angle)
    out = []
    for i in range(count):
        t = 2 * math.pi * i / count
        x, y = rx * math.cos(t), ry * math.sin(t)
        out.append(Vector((cx + x * ca - y * sa, cy + x * sa + y * ca, z)))
    return out


def superellipse(cx, cy, rx, ry, power=2.0, count=48, angle=0.0):
    """A closed outline [(x, y)], counter-clockwise: a superellipse (power 2: an ellipse; higher: boxier),
    turned by `angle` (radians) about its centre."""
    ca, sa = math.cos(angle), math.sin(angle)
    out = []
    for i in range(count):
        t = 2 * math.pi * i / count
        c, s_ = math.cos(t), math.sin(t)
        x = math.copysign(abs(c) ** (2 / power), c) * rx
        y = math.copysign(abs(s_) ** (2 / power), s_) * ry
        out.append((cx + x * ca - y * sa, cy + x * sa + y * ca))
    return out


def surface_z(objects, x, y, default=0.0):
    """The height of the highest of objects' surfaces over (x, y) (a ray cast down)."""
    best = None
    depsgraph = bpy.context.evaluated_depsgraph_get()
    for obj in objects:
        ok, loc, _nrm, _i = obj.evaluated_get(depsgraph).ray_cast(Vector((x, y, 500.0)), Vector((0, 0, -1)))
        if ok and (best is None or loc.z > best):
            best = loc.z
    return default if best is None else best


def delete_faces(obj, fn):
    """Deletes the faces fn(centre, normal) picks (parts nobody sees)."""
    sh.apply_modifiers(obj)
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.normal_update()
    doomed = [f for f in bm.faces if fn(f.calc_center_median(), f.normal)]
    bmesh.ops.delete(bm, geom=doomed, context="FACES")
    bm.to_mesh(obj.data)
    bm.free()
    return obj


def join(objects, name=None):
    """Joins meshes into one (fewer parts)."""
    objs = [o for o in objects if o is not None]
    if len(objs) < 2:
        return objs[0] if objs else None
    with bpy.context.temp_override(active_object=objs[0], selected_editable_objects=objs, object=objs[0]):
        bpy.ops.object.join()
    if name:
        objs[0].name = name
    return objs[0]


def flatten_under(objects, z=0.0):
    """Cuts away what lies below z (closing the cut): parts standing on their layer."""
    return sh.flat_bottom(objects, z)


def bisect_mesh(obj, cuts_x=(), cuts_y=()):
    """Splits obj's faces along vertical planes x = c and y = c (more faces to paint by the sprite)."""
    sh.apply_modifiers(obj)
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    for axis, cuts in ((0, cuts_x), (1, cuts_y)):
        for c in cuts:
            geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
            bmesh.ops.bisect_plane(bm, geom=geom, dist=1e-5, plane_co=(c, 0, 0) if axis == 0 else (0, c, 0),
                                   plane_no=(1, 0, 0) if axis == 0 else (0, 1, 0))
    bm.to_mesh(obj.data)
    bm.free()
    return obj


def rotate_z(objects, degrees, pivot=(0.0, 0.0)):
    m = Matrix.Translation((pivot[0], pivot[1], 0)) @ Matrix.Rotation(math.radians(degrees), 4, "Z") @ \
        Matrix.Translation((-pivot[0], -pivot[1], 0))
    for obj in objects:
        obj.data.transform(m)
    return objects
