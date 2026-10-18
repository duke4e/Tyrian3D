"""The purple fighter of DELI, BONUS, New Deli and VAULT (sheet U sprite 45, 2x2: 24 x 28 pixels; sky
layer; its animation 45 47 49 51 49 47), polished (2026-10-18; it replaces misc.py's purple_fighter(), a
flat grey plate in the sprite's outline with a red lump). models.cfg: sprite u 45 purple_fighter yaw=0,
frame u 47 purple_fighter_47, frame u 49 purple_fighter_49, frame u 51 purple_fighter_51.

As the 4x upscale draws it, nose down the screen: a domed purple body like a shield (the sprite's ramp 5,
columns 1-22 of rows 11-27): straight across its back (row 11, columns 4-19), its upper corners cut off
(rows 12-14), widest over rows 15-20, then narrowing to a point (row 27); a plate lies over its back, its
arched front edge the sprite's bright arc (rows 12-13). Down its middle three slits glow red (rows 13, 15
and 17, wider towards the front), and in its nose a dark mouth (columns 9-14 of rows 19-25) holds two
salmon mandibles (ramp 4, columns 10 and 13); salmon studs sit on its shoulders (columns 5-6 and 17-18 of
row 12). At its back two engines with salmon rims (columns 8-10 and 13-15 of rows 9-10) blow red flames up
the screen (ramp 7, rows 4-8).

The animation is the engines' fire: in 45 two short flames (to row 4), in 47 longer and thinner (to row
2), in 49 a crown of fire (to row 1, side tongues spreading out to columns 4 and 19, the gap between the
flames filled, orange-yellow at their roots), in 51 long flames with small side tongues; the slits glow
brighter with it (0x72-0x74 in 45 and 47, 0x74-0x76 in 49, 0x76-0x7a in 51). Each tongue of fire is
built in three layers, a red outer one, a brighter one inside it and a hot one at its root, each showing
on top of the one round it, as the sprite's flames are brightest down their middles. One model per frame:
purple_fighter (45), purple_fighter_47, purple_fighter_49 and purple_fighter_51: the same body, each
with its frame's flames and glow. The flames lie within the body's height, so every frame has the same
bounds in height and the game, which centres sky objects in height, centres them alike.

The sprite is symmetric about the edge between its columns 11 and 12 (x = 0 here): the model is built
about x = 0 and its left parts mirrored. Origin at the sprite's centre (pixel 12, 14); +Y up the sprite,
+Z towards the camera.

Replaces misc.py's purple_fighter() and PURPLE_FIGHTER: remove them (and the call) so that it doesn't
overwrite these models.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (each frame's
silhouette against enemy_U.png), --preview <prefix>.
"""
import math
import os
import sys

import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
from polish_jets import Curve, chaikin  # noqa: E402

# The body along y, nose to back: its half-width (the sprite's outline about two thirds covered) and its
# crown's height on the middle line; the height its sides come down to, its flat underside.
BODY_Y = (-13.7, 2.67)
BODY_HALF = Curve([(-13.7, 0.0), (-13.3, 1.15), (-12.5, 2.75), (-11.5, 4.55), (-10.5, 5.95), (-9.5, 7.3),
                   (-8.5, 8.55), (-7.5, 9.55), (-6.5, 10.35), (-5.2, 10.7), (-2.3, 10.7), (-1.5, 10.5),
                   (-0.8, 9.85), (0.0, 8.85), (0.8, 7.95), (1.6, 7.7), (2.67, 7.67)])
BODY_TOP = Curve([(-13.7, 1.55), (-12.0, 2.35), (-9.0, 3.4), (-6.0, 4.15), (-3.0, 4.75), (0.0, 5.2), (1.4, 5.3),
                  (2.2, 5.2), (2.67, 4.95)])
BODY_EQUATOR, BODY_BOTTOM, BODY_POWER, BACK_ROUND = 1.3, 0.35, 2.3, 1.1

# The slits down the middle (rows 13, 15 and 17): y, half-length across, the glowing core's half-length
# (row 13's is dark in 45, red from 47 on).
SLITS = [(0.5, 1.2, 0.9), (-1.5, 2.15, 1.2), (-3.5, 3.1, 2.15)]
SLIT_WIDTH = 0.85  # across y

# The mouth in the nose (columns 9-14 of rows 19-25): its outline, and the mandibles in it (columns 10 and
# 13), each through points (x, y) from its root to its tip.
MOUTH = [(0.0, -5.45), (1.7, -5.6), (2.65, -6.2), (2.75, -8.0), (2.45, -9.8), (1.9, -11.2), (1.05, -12.2),
         (0.0, -12.45)]
MANDIBLE = [(1.1, -5.95), (1.55, -6.9), (1.8, -8.1), (1.78, -9.3), (1.6, -10.3), (1.42, -11.0)]
MANDIBLE_RADII = [0.36, 0.44, 0.42, 0.34, 0.22, 0.06]

# The engines (columns 8-10 and 13-15 of rows 9-10): their axis' x and z, radius, from y to y (their
# rims at the back), and the bridge between them.
ENGINE_X, ENGINE_Z, ENGINE_R, ENGINE_Y = 2.55, 3.35, 1.62, (0.6, 4.85)
BRIDGE = (2.6, 0.5, 4.3, 1.4, 4.3)  # half-width, from y, to y, from z, to z
# The shoulder studs (columns 5-6 and 17-18 of row 12): middle (x, y), radii.
STUD, STUD_RADII = (6.05, 1.55), (0.9, 0.7, 0.5)
# The plate over the body's back (rows 11-13, its lit front edge the sprite's bright arc): its front edge
# along x (an arc, highest in the middle), how far it stands above the body.
PLATE_FRONT = Curve([(0.0, 1.05), (2.5, 0.95), (4.5, 0.6), (6.2, 0.05), (7.3, -0.6)])
PLATE_HALF, PLATE_LIFT = 7.35, 0.32

# The frames: (model, sprite, flames [(path [(x, y)] from the root up, the half-widths along it, the
# tongue's half-height)], the colours (palette index, emission strength) of the flames' layers (the
# outer tongue, the middle one and the hot inner one) and of the slits' glowing cores (rows 17, 15 and
# 13; row 13's is dark in 45)).
FLAME_Z = 3.35
# The flames' layers: (name, the share of the tongue's length they reach, of its width, of its height):
# each inner layer narrower and shorter but a little taller, so that it shows on top of the outer.
FLAME_LAYERS = [("flame_tip", 1.0, 1.0, 1.0), ("flame_mid", 0.7, 0.66, 1.12), ("flame_hot", 0.42, 0.4, 1.22)]
FRAMES = [
    ("purple_fighter", 45,
     [([(2.55, 4.6), (2.65, 6.0), (2.6, 7.4), (2.45, 8.7), (2.5, 9.95)], [1.45, 1.55, 1.25, 0.65, 0.0], 1.15)],
     {"flame_tip": (0x73, 1.0), "flame_mid": (0x74, 1.25), "flame_hot": (0x75, 1.6),
      "slit_core": (0x74, 1.1), "slit": (0x72, 0.85), "slit_front": (0x51, 0.0)}),
    ("purple_fighter_47", 47,
     [([(2.55, 4.6), (2.7, 6.2), (2.65, 7.9), (2.45, 9.7), (2.5, 11.95)], [1.4, 1.5, 1.1, 0.55, 0.0], 1.1)],
     {"flame_tip": (0x74, 1.05), "flame_mid": (0x75, 1.35), "flame_hot": (0x77, 1.75),
      "slit_core": (0x74, 1.15), "slit": (0x73, 0.9), "slit_front": (0x72, 0.8)}),
    ("purple_fighter_49", 49,
     [([(2.4, 4.6), (2.15, 6.2), (2.3, 8.0), (2.6, 10.1), (2.5, 12.9)], [1.75, 1.95, 1.4, 0.7, 0.0], 1.3),
      ([(3.4, 4.9), (4.55, 6.0), (5.65, 7.3), (6.65, 8.8), (7.45, 10.75)], [0.95, 1.0, 0.72, 0.4, 0.0], 0.8),
      ([(1.2, 4.8), (0.85, 6.2), (0.5, 7.3)], [1.2, 0.95, 0.0], 0.85)],
     {"flame_tip": (0x73, 1.1), "flame_mid": (0x76, 1.45), "flame_hot": (0x7a, 2.0),
      "slit_core": (0x76, 1.3), "slit": (0x74, 1.0), "slit_front": (0x72, 0.85)}),
    ("purple_fighter_51", 51,
     [([(2.55, 4.6), (2.65, 6.1), (2.6, 7.8), (2.45, 9.6), (2.5, 11.95)], [1.5, 1.55, 1.15, 0.58, 0.0], 1.15),
      ([(3.5, 5.0), (4.5, 5.9), (5.4, 7.0), (6.3, 8.35)], [0.8, 0.75, 0.42, 0.0], 0.68)],
     {"flame_tip": (0x73, 1.05), "flame_mid": (0x74, 1.35), "flame_hot": (0x77, 1.75),
      "slit_core": (0x79, 1.45), "slit": (0x76, 1.1), "slit_front": (0x72, 0.85)}),
]


# --- Helpers ----------------------------------------------------------------------------------------

def end_round(y, y0, y1, r0, r1):
    """1 inside [y0, y1], falling on a quarter circle to 0 within r0 of y0 and r1 of y1."""
    f = 1.0
    for d, r in ((y - y0, r0), (y1 - y, r1)):
        if r > 0 and d < r:
            f = min(f, math.sqrt(max(0.0, 1 - (1 - max(d, 0.0) / r) ** 2)))
    return f


def body_section(y):
    """The body's half-width and the crown's height above the equator at y (the back end rounded)."""
    f = end_round(y, BODY_Y[0], BODY_Y[1], 0.0, BACK_ROUND)
    # The back edge is straight across (row 11): its corners only a little rounded, its top more.
    return BODY_HALF(y) * (0.82 + 0.18 * f), (BODY_TOP(y) - BODY_EQUATOR) * (0.35 + 0.65 * f)


def body_top(x, y):
    """The height of the body's top at (x, y)."""
    hw, top = body_section(y)
    if hw <= 0.02 or abs(x) >= hw:
        return BODY_EQUATOR
    return BODY_EQUATOR + top * (1 - (abs(x) / hw) ** BODY_POWER) ** (1 / BODY_POWER)


def paint(obj, mats, key):
    keys = [key(poly) for poly in obj.data.polygons]
    names = []
    for name in keys:
        if name not in names:
            names.append(name)
    obj.data.materials.clear()
    for name in names:
        obj.data.materials.append(mats[name])
    for poly, name in zip(obj.data.polygons, keys):
        poly.material_index = names.index(name)
    return obj


def mirrored(obj):
    copy = k.mirror_x(obj, obj.name + "_r")
    copy.data.name = copy.name
    return k.smooth(copy, 50)


def pad(name, outline, mat, lift=0.12, sink=0.5, thickness=None, dome=0.05):
    """A thin plate lying on the body's top: the polygon outline (counter-clockwise), its top `lift`
    above the surface, its bottom `sink` below; rounded off at its edge."""
    n = len(outline)
    cx, cy = sum(p[0] for p in outline) / n, sum(p[1] for p in outline) / n
    rings = []
    for f, dz in ((1.0, -sink), (1.0, lift - 0.06), (0.93, lift), (0.5, lift + dome)):
        ring = []
        for x, y in outline:
            px, py = cx + (x - cx) * f, cy + (y - cy) * f
            ring.append(Vector((px, py, body_top(px, py) + dz)))
        rings.append(ring)
    verts = [v for r in rings for v in r]
    faces = []
    for r in range(len(rings) - 1):
        for i in range(n):
            j = (i + 1) % n
            faces.append((r * n + i, r * n + j, (r + 1) * n + j, (r + 1) * n + i))
    verts.append(Vector((cx, cy, body_top(cx, cy) + lift + dome)))
    top = (len(rings) - 1) * n
    faces += [(top + i, top + (i + 1) % n, len(verts) - 1) for i in range(n)]
    verts.append(Vector((cx, cy, body_top(cx, cy) - sink)))
    faces += [((i + 1) % n, i, len(verts) - 1) for i in range(n)]
    obj = k.mesh_object(name, verts, faces, mat)
    k.recalc_normals(obj)
    return k.smooth(obj, 50)


def capsule(cx, cy, half_x, half_y, count=24):
    """A stadium's outline round (cx, cy): half_x across, half_y along y, counter-clockwise."""
    out = []
    r = half_y
    straight = max(half_x - r, 0.0)
    for i in range(count):
        a = 2 * math.pi * i / count
        c, s = math.cos(a), math.sin(a)
        out.append((cx + math.copysign(straight, c) * (abs(c) > 1e-9) + r * c, cy + r * s))
    return out


def tube(name, points, radii, mat, segments=10, squash=1.0):
    """A round tube through 3D points with a radius at each, closed to points at its ends."""
    rings = []
    for i, p in enumerate(points):
        a, b = points[max(i - 1, 0)], points[min(i + 1, len(points) - 1)]
        t = (b - a).normalized()
        side = t.cross(Vector((0, 0, 1)))
        if side.length < 1e-6:
            side = Vector((1, 0, 0))
        side.normalize()
        up = side.cross(t).normalized()
        r = max(radii[i], 0.02)
        angles = [2 * math.pi * j / segments for j in range(segments)]
        rings.append([p + (side * math.cos(a) + up * squash * math.sin(a)) * r for a in angles])
    t0 = (points[1] - points[0]).normalized()
    t1 = (points[-1] - points[-2]).normalized()
    obj = k.loft(name, rings, mat, start_point=points[0] - t0 * radii[0] * 0.7,
                 end_point=points[-1] + t1 * max(radii[-1], 0.02) * 0.7)
    return k.smooth(obj, 60)


# --- The parts (left side where mirrored) ------------------------------------------------------------

def body(mats):
    y0, y1 = BODY_Y
    ys = [y0 + (y1 - y0) * i / 40 for i in range(1, 40)]
    ys += [y1 - BACK_ROUND * (1 - math.cos(math.pi / 2 * i / 5)) for i in range(5)]
    ys = sorted(set(round(y, 4) for y in ys))
    rings = []
    for y in ys:
        hw, top = body_section(y)
        rings.append(k.ring(y, max(hw, 0.05), 1.0, 40, z=BODY_EQUATOR, top=max(top, 0.05),
                            bottom=BODY_EQUATOR - BODY_BOTTOM, power=BODY_POWER))
    obj = k.loft("body", rings, mats["body"], start_point=(0, y0, BODY_EQUATOR + 0.2),
                 end_point=(0, y1, BODY_EQUATOR + 1.0))
    return k.smooth(obj, 55)


def slits(mats):
    """The three slits down the middle: a dark rim lying in the top, a glowing core in it."""
    out = []
    for i, (y, half, core) in enumerate(SLITS):
        out.append(pad(f"slit{i}", capsule(0.0, y, half, SLIT_WIDTH / 2), mats["slit_rim"], lift=0.1, sink=0.6))
        key = "slit_front" if i == 0 else "slit_core" if i == 2 else "slit"  # rows 13, 15, 17
        out.append(pad(f"slit_core{i}", capsule(0.0, y, core, SLIT_WIDTH / 2 * 0.62), mats[key], lift=0.16, sink=0.3,
                       dome=0.02))
    return out


def mouth(mats):
    """The dark mouth in the nose and the mandibles in it."""
    outline = MOUTH + [(-x, y) for x, y in reversed(MOUTH[1:-1])]
    outline = chaikin(outline[::-1], 2)  # counter-clockwise, its corners rounded
    parts = [pad("mouth", outline, mats["mouth"], lift=0.08, sink=0.5, dome=-0.15)]
    # The ridge at its top between the mandibles (rows 19-21), purple.
    parts.append(pad("mouth_ridge", capsule(0.0, -6.35, 0.72, 0.72, 16), mats["engine"], lift=0.22, sink=0.3))
    pts = [Vector((x, y, body_top(x, y) + 0.3)) for x, y in MANDIBLE]
    m = tube("mandible", pts, MANDIBLE_RADII, mats["salmon"], 10, squash=0.8)
    m.data.materials.append(mats["salmon_dark"])
    for poly in m.data.polygons:
        if poly.center.y < -9.4:
            poly.material_index = 1
    parts.append(m)
    parts.append(mirrored(m))
    return parts


def engines(mats):
    """The two engines at the back: round cans along y with salmon rims, the bridge between them."""
    parts = []
    y0, y1 = ENGINE_Y
    r = ENGINE_R
    profile = [(y0, r * 0.9), (y0 + 0.5, r), (y1 - 0.75, r), (y1 - 0.55, r + 0.1), (y1 - 0.2, r + 0.12), (y1, r - 0.15),
               (y1 - 0.05, r - 0.42), (y1 - 0.5, r - 0.5), (y1 - 0.55, 0.0)]
    can = k.lathe("engine", [(y, rr) for y, rr in profile], None, segments=20, axis_x=-ENGINE_X, axis_z=ENGINE_Z)
    n = 20
    # Ring pairs: 0-1 the can, 2-5 the rim, 6 the bore's wall; then the fans closing the can's front
    # (inside the body) and the bore (the fire's root, glowing).
    keys = ["engine"] * 2 + ["salmon"] * 4 + ["flame_hot"]

    def key(poly):
        pair = poly.index // n
        if pair < len(keys):
            return keys[pair]
        return "engine" if pair == len(keys) else "flame_hot"
    paint(can, mats, key)
    k.smooth(can, 50)
    parts += [can, mirrored(can)]
    hw, ya, yb, za, zb = BRIDGE
    bridge = k.box("bridge", (0.0, (ya + yb) / 2, (za + zb) / 2), (2 * hw, yb - ya, zb - za), mats["engine"])
    k.bevel(bridge, 0.45, 2)
    parts.append(bridge)
    return parts


def studs(mats):
    (x, y), (rx, ry, h) = STUD, STUD_RADII
    stud = k.ellipsoid("stud", (-x, y, body_top(-x, y) - 0.15), (rx, ry, h + 0.15), mats["stud"], 16, 8)
    k.smooth(stud, 60)
    return [stud, mirrored(stud)]


def plate(mats):
    """The plate over the body's back, from its back edge to an arched front edge, standing a little
    proud of the body (its lit front edge is the sprite's bright arc)."""
    right = []
    for i in range(13):  # the front edge, from the middle out
        x = PLATE_HALF * i / 12
        right.append((x, PLATE_FRONT(x)))
    y_back = BODY_Y[1] - 0.25
    for i in range(1, 7):  # round the shoulder to the back edge
        a = (math.pi / 2) * i / 6
        front = PLATE_FRONT(PLATE_HALF)
        right.append((PLATE_HALF - 0.9 * (1 - math.cos(a)), front + (y_back - front) * math.sin(a)))
    right.append((0.0, y_back))
    outline = right + [(-x, y) for x, y in reversed(right[1:-1])]
    # counter-clockwise: the front edge runs left to right... the right half goes out along the front
    # and back along the rear, which is counter-clockwise for the right half; the mirrored half closes it.
    return pad("plate", outline, mats["body"], lift=PLATE_LIFT, sink=0.6, dome=0.06)


def flames(spec, mats):
    """The engines' fire: tongues along paths in plan (at FLAME_Z), their half-widths along them and
    their half-height, each in three layers (FLAME_LAYERS): the outer tongue red, a middle one inside it
    and a hot one at the root, each showing on top of the one round it, as the sprite's flames are
    brightest down their middles and at their roots. Built for the left engine and mirrored."""
    parts = []
    segments = 10
    for i, (path, widths, height) in enumerate(spec):
        pts = [Vector((-x, y, FLAME_Z)) for x, y in path]
        # The path smoothed (Catmull-Rom through its points), the widths along it.
        dense, dense_w = [], []
        for s in range(len(pts) - 1):
            p0, p1 = pts[max(s - 1, 0)], pts[s]
            p2, p3 = pts[s + 1], pts[min(s + 2, len(pts) - 1)]
            for j in range(8):
                t = j / 8
                t2, t3 = t * t, t * t * t
                dense.append(0.5 * (2 * p1 + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 +
                                    (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
                dense_w.append(widths[s] + (widths[s + 1] - widths[s]) * (3 * t2 - 2 * t3))
        dense.append(pts[-1])
        dense_w.append(widths[-1])
        lengths = [0.0]
        for a, b in zip(dense, dense[1:]):
            lengths.append(lengths[-1] + (b - a).length)
        total = lengths[-1]

        def at(d):
            """The point, direction and half-width at distance d along the tongue."""
            last = len(dense) - 2
            j = max(0, min(last, next((n for n in range(last + 1) if lengths[n + 1] >= d), last)))
            f = (d - lengths[j]) / max(lengths[j + 1] - lengths[j], 1e-6)
            p = dense[j].lerp(dense[j + 1], f)
            return p, (dense[j + 1] - dense[j]).normalized(), dense_w[j] + (dense_w[j + 1] - dense_w[j]) * f

        wmax = max(widths)
        for name, reach, wide, tall in FLAME_LAYERS:
            end = total * reach
            count = max(5, int(round(15 * reach)))
            rings = []
            for j in range(count):
                d = end * j / count
                p, t, w = at(d)
                # The inner layers taper to their own tips (their width falls to 0 at their end).
                if reach < 1.0:
                    w = w * wide * (1 - (d / end) ** 2.2) ** 0.6
                w = max(w, 0.03)
                h = height * tall * min(1.0, w / (wmax * wide)) ** 0.6
                side = Vector((-t.y, t.x, 0.0)).normalized()
                ring = []
                for m in range(segments):
                    ang = 2 * math.pi * m / segments
                    c, sn = math.cos(ang), math.sin(ang)
                    ring.append(p + side * w * math.copysign(abs(c) ** 0.8, c) + Vector((0, 0, h * sn)))
                rings.append(ring)
            tip, _, _ = at(end)
            root = dense[0] - (dense[1] - dense[0]).normalized() * 0.3
            obj = k.loft(f"{name}{i}", rings, mats[name], start_point=root, end_point=tip)
            k.smooth(obj, 60)
            parts += [obj, mirrored(obj)]
    return parts


def materials(colours):
    pal = k.level_palette()
    m = {
        "body": k.material("pfighter_body", palette=0x58, metallic=0.35, roughness=0.32),
        "engine": k.material("pfighter_engine", palette=0x55, metallic=0.4, roughness=0.35),
        "slit_rim": k.material("pfighter_slit", palette=0x51, metallic=0.2, roughness=0.6),
        "mouth": k.material("pfighter_mouth", palette=0x60, metallic=0.2, roughness=0.6),
        "salmon": k.material("pfighter_salmon", palette=0x49, metallic=0.3, roughness=0.32),
        "salmon_dark": k.material("pfighter_salmon_dark", palette=0x45, metallic=0.3, roughness=0.4),
        "stud": k.material("pfighter_stud", palette=0x4a, roughness=0.3, emission=pal[0x49], emission_strength=0.35),
    }
    for key, (index, strength) in colours.items():
        if strength > 0:  # fire and glowing slits: no gloss
            m[key] = k.material(f"pfighter_{key}_{index:x}", palette=index, roughness=0.85, emission=pal[index],
                                emission_strength=strength)
        else:
            m[key] = k.material(f"pfighter_{key}_{index:x}", palette=index, metallic=0.2, roughness=0.6)
    return m


def build_model(spec, colours):
    k.reset()
    mats = materials(colours)
    body(mats)
    slits(mats)
    mouth(mats)
    engines(mats)
    studs(mats)
    plate(mats)
    flames(spec, mats)


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


def bounds():
    depsgraph = bpy.context.evaluated_depsgraph_get()
    zs = []
    for obj in bpy.context.scene.objects:
        if obj.type == "MESH":
            evaluated = obj.evaluated_get(depsgraph)
            mesh = evaluated.to_mesh()
            zs += [(obj.matrix_world @ v.co).z for v in mesh.vertices]
            evaluated.to_mesh_clear()
    return min(zs), max(zs)


def build():
    options = k.args()
    outdir = options.get("outdir", os.path.join(HERE, "..", "..", "..", "..", "assets", "models", "enemies"))
    only = options["only"].split(",") if "only" in options else None
    for name, sprite, spec, colours in FRAMES:
        if only and name not in only:
            continue
        build_model(spec, colours)
        used = {m.name for o in bpy.context.scene.objects if o.type == "MESH" for m in o.data.materials}
        print("== %s (U %d): %d triangles, %d materials, z %.2f to %.2f: %s" % (
            name, sprite, triangles(), len(used), *bounds(), ", ".join(sorted(used))))
        if "check" in options:
            sheet = options["check"]
            k.check_silhouette(os.path.join(sheet, "enemy_U.png") if os.path.isdir(sheet) else sheet, sprite)
        bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
        path = os.path.join(outdir, name + ".glb")
        k.export(path)
        print("%s: %.1f KB" % (path, os.path.getsize(path) / 1024))
        if "preview" in options:
            k.preview(options["preview"] + name)


if __name__ == "__main__":
    build()
