"""The grey and blue squid ship of CAMANIS, ICE EXIT and DIG SITE (sheet 7 sprite 237, 2x2: 24 x 28 pixels; sky
layer; its animation 237 275 239 275), polished (2026-10-19; it replaces wave2_h.py's squid_ship()). models.cfg:
sprite 7 237 squid_ship yaw=0, frame 7 275 squid_ship_275, frame 7 239 squid_ship_239.

The same craft flying the other way is the "beacon frame" (sheet 7 sprite 51, animation 51 89 127 89): its
three frames are this sprite's three frames flipped upside down and moved a pixel left (pixel for pixel), and
as the ship is symmetric about its column 12, that is the ship turned round about the sprite's centre: so
the beacon is these models turned round (models.cfg: sprite 7 51 squid_ship yaw=180, frame 7 89
squid_ship_275, frame 7 127 squid_ship_239), its "lamp" this engine's flame. No other enemy shows any of
these six sprites.

As the 4x upscale draws it, hood up the screen and engine down:
- a grey hood like a pointed helmet (rows 0-10), a raised spine down its middle (columns 11-13) between two
  grooves, a groove across its flanks (row 6) and a blue gill on either lower flank (columns 7-9 and 15-16,
  rows 7-10), its light streak down the middle;
- a thin blue blade across the whole sprite under it (row 11), pointed at both ends;
- under the blade a grey jaw (rows 12-14) holding a blue faceted crystal (rows 13-19), a light ridge down it;
- two tendrils hanging from the blade (from columns 5-6 and 18-19), blue where they leave it, bowing out to
  columns 3 and 21 and turning grey as they come down (rows 18-22), curling in at their ends (row 23)
  towards the engine;
- the engine (rows 20-24): a dark cowl with five grey ribs along it, the outer two running on beside the
  exhaust as guards; and the flame (from row 23).

The animation is the engine's flame: in 237 a small red glow (rows 23-25, its core 0x7a), in 275 a bigger
one with a yellow core (rows 23-26, 0x7d), in 239 a large fire, white-hot at its core (rows 23-27, seven
pixels wide at its root, 0x7f). One model per frame: squid_ship (237), squid_ship_275 and squid_ship_239, the
same ship with its frame's flame. The flame lies within the ship's height, so every frame has the same
bounds in height and the game, which centres sky objects in height, centres them alike. Each layer of fire
(an outer red tongue, a brighter one inside it and a hot core) glows in its own palette colour.

The sprite is symmetric about its column 12's centre (x 0.5 here): the ship is built about u = 0 (u = x -
AXIS_X) and moved there; its left parts are mirrored. Origin at the sprite's centre (pixel 12, 14); +Y up the
sprite, +Z towards the camera.

Replaces wave2_h.py's squid_ship() and SQUID_AXIS (and its MODELS entry) and wave2_f.py's beacon_frame() and
BEACON (the beacon is this ship turned round): remove them so that they don't overwrite these models.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir or enemy_7.png> (each
frame's silhouette against its sprite), --preview <prefix>, --only <name,...>.
"""
import math
import os
import sys

import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
from polish_redjet import Curve, chaikin, end_round, facet, resample  # noqa: E402

AXIS_X = 0.5

# --- The hood ------------------------------------------------------------------------------------------
# Along y: its half-width in plan (2/3 into the sprite's outline, the staircase of its edges smoothed) and
# the height of its crown above its rim; its underside lies HOOD_UNDER below the rim.
HOOD_TIP, HOOD_END = 13.75, 2.65
HOOD = Curve([(2.65, 0.0, 0.2), (2.75, 5.8, 1.0), (3.0, 7.6, 2.2), (3.4, 8.4, 3.2), (4.2, 8.65, 3.75),
              (5.5, 8.0, 4.05), (6.5, 7.7, 4.15), (7.5, 7.6, 4.15), (8.5, 7.3, 4.0), (9.5, 6.5, 3.75),
              (10.5, 5.5, 3.35), (11.5, 4.45, 2.8), (12.5, 3.2, 2.1), (13.0, 2.55, 1.65), (13.4, 1.95, 1.2),
              (13.62, 1.3, 0.8), (13.75, 0.0, 0.45)])
HOOD_UNDER, HOOD_POWER = 0.8, 1.9
SPINE_HALF = 1.35        # the spine (columns 11-13)
GROOVE_U = 1.95          # the grooves either side of it (columns 10 and 14)
ACROSS_Y = 7.5           # the groove across the flanks (row 6)
GILL = (2.6, 5.45, 3.35, 6.9)   # the gills: |u| from, to; y from, to (columns 7-9, rows 7-10)


def hood_section(y):
    hw, top = HOOD(y)
    return max(hw, 0.0), max(top, 0.0)


def hood_top(u, y):
    """The hood's top surface at (u, y) (its rim height outside it)."""
    hw, top = hood_section(y)
    if hw <= 0.05 or abs(u) >= hw:
        return 0.0
    return top * (1 - (abs(u) / hw) ** HOOD_POWER) ** (1 / HOOD_POWER)


def spine_top(y):
    return hood_top(0.0, y) + 0.5 * end_round(y, 1.6, 13.25, 0.9, 0.8)


# --- The parts below the hood --------------------------------------------------------------------------
WING_Y, WING_Z, WING_SPAN = 2.45, 0.75, 11.17    # the blade across (row 11), 2/3 into columns 1 and 23
# The crystal (rows 13-19): its half-width in plan along y, its ridge's height.
CRYSTAL = Curve([(-6.3, 0.0, 1.2), (-5.7, 2.0, 1.9), (-4.5, 2.7, 2.45), (-3.5, 3.75, 2.85), (-2.6, 4.3, 3.05),
                 (-1.6, 3.65, 3.05), (-0.5, 2.6, 2.9), (0.6, 1.6, 2.6), (1.1, 0.0, 2.3)])
CRYSTAL_Y = (-6.3, 1.1)
# The left tendril's middle line (u, y, z) from under the blade to its curled end, and its radius along it.
TENDRIL = [(-6.25, 2.2, 0.75), (-6.05, 1.0, 0.75), (-6.4, -0.4, 0.72), (-7.35, -1.6, 0.68), (-8.15, -2.8, 0.62),
           (-8.65, -4.0, 0.56), (-8.95, -5.4, 0.5), (-9.05, -6.8, 0.45), (-8.95, -8.0, 0.42), (-8.45, -9.05, 0.4),
           (-7.5, -9.65, 0.4), (-6.45, -9.75, 0.42), (-5.8, -9.6, 0.45)]
TENDRIL_RADII = [1.3, 1.35, 1.35, 1.32, 1.28, 1.22, 1.18, 1.15, 1.12, 1.08, 1.0, 0.85, 0.6]
TENDRIL_GREY_Y = -4.3     # grey below this (rows 18-23), blue above
# The engine (rows 20-24): the cowl's ends along y, half-width, half-height, axis height; the ribs' u.
COWL_Y, COWL_HALF, COWL_HEIGHT, ENGINE_Z = (-9.15, -6.3), 4.55, 2.0, 1.0
RIBS_U = (-2.0, 0.0, 2.0)
GUARD_U, GUARD_END = 4.0, -11.95  # the outer ribs run on beside the flame to row 24
NOZZLE_Y = -9.15

# The frames: (model, sprite, the flame's outline along -y [(distance from the nozzle, half-width)], the
# palette index and emission strength of its layers (outer, middle, core)).
FLAME_Z = ENGINE_Z
FLAME_LAYERS = [("flame_outer", 1.0, 1.0, 1.0), ("flame_mid", 0.74, 0.7, 1.12), ("flame_core", 0.46, 0.45, 1.24)]
FLAME_ROOT = -9.3    # the flame's root (row 23's top edge, inside the nozzle)
FRAMES = [
    ("squid_ship", 237, [(0.0, 1.0), (0.5, 1.6), (1.2, 2.45), (1.8, 2.3), (2.35, 1.45), (2.7, 0.0)],
     {"flame_outer": (0x75, 1.0), "flame_mid": (0x77, 1.3), "flame_core": (0x7a, 1.7)}),
    ("squid_ship_275", 275, [(0.0, 2.2), (0.6, 2.45), (1.6, 2.5), (2.5, 2.35), (3.2, 1.5), (3.7, 0.0)],
     {"flame_outer": (0x76, 1.05), "flame_mid": (0x7a, 1.4), "flame_core": (0x7d, 1.9)}),
    ("squid_ship_239", 239, [(0.0, 3.2), (0.7, 3.5), (1.5, 3.3), (2.3, 2.6), (3.2, 2.4), (4.1, 1.4), (4.7, 0.0)],
     {"flame_outer": (0x77, 1.1), "flame_mid": (0x7b, 1.5), "flame_core": (0x7f, 2.0)}),
]


# --- Helpers ---------------------------------------------------------------------------------------------

def mirrored(obj, angle=50):
    copy = k.mirror_x(obj, obj.name + "_r")
    copy.data.name = copy.name
    return k.smooth(copy, angle)


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
        rings.append([p + (side * math.cos(2 * math.pi * j / segments) + up * squash * math.sin(2 * math.pi * j / segments)) * r
                      for j in range(segments)])
    t0 = (points[1] - points[0]).normalized()
    t1 = (points[-1] - points[-2]).normalized()
    obj = k.loft(name, rings, mat, start_point=points[0] - t0 * radii[0] * 0.7,
                 end_point=points[-1] + t1 * max(radii[-1], 0.02) * 0.7)
    return k.smooth(obj, 60)


def catmull(points, step=0.35):
    """A smooth path through 3D points (Catmull-Rom), about `step` apart."""
    pts = [Vector(p) for p in points]
    out = []
    for s in range(len(pts) - 1):
        p0, p1 = pts[max(s - 1, 0)], pts[s]
        p2, p3 = pts[s + 1], pts[min(s + 2, len(pts) - 1)]
        count = max(1, int(round((p2 - p1).length / step)))
        for j in range(count):
            t = j / count
            t2, t3 = t * t, t * t * t
            out.append(0.5 * (2 * p1 + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 +
                              (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
    out.append(pts[-1])
    return out


def surface_pad(name, outline, surface, mat, lift=0.1, sink=0.5, dome=0.05):
    """A thin plate lying on a surface (surface(u, y) its height): the polygon outline (counter-clockwise
    seen from above), its top `lift` above the surface, rounded off at its edge, closed underneath."""
    n = len(outline)
    cx, cy = sum(p[0] for p in outline) / n, sum(p[1] for p in outline) / n
    rings = []
    for f, dz in ((1.0, -sink), (1.0, lift - 0.06), (0.9, lift), (0.45, lift + dome)):
        rings.append([Vector((cx + (x - cx) * f, cy + (y - cy) * f, surface(cx + (x - cx) * f, cy + (y - cy) * f) + dz))
                      for x, y in outline])
    verts = [v for r in rings for v in r]
    faces = []
    for r in range(len(rings) - 1):
        for i in range(n):
            j = (i + 1) % n
            faces.append((r * n + i, r * n + j, (r + 1) * n + j, (r + 1) * n + i))
    verts.append(Vector((cx, cy, surface(cx, cy) + lift + dome)))
    top = (len(rings) - 1) * n
    faces += [(top + i, top + (i + 1) % n, len(verts) - 1) for i in range(n)]
    verts.append(Vector((cx, cy, surface(cx, cy) - sink)))
    faces += [((i + 1) % n, i, len(verts) - 1) for i in range(n)]
    obj = k.mesh_object(name, verts, faces, mat)
    k.recalc_normals(obj)
    return k.smooth(obj, 50)


def ccw(outline):
    """The outline counter-clockwise seen from above."""
    area = sum(outline[i][0] * outline[(i + 1) % len(outline)][1] - outline[(i + 1) % len(outline)][0] * outline[i][1]
               for i in range(len(outline)))
    return outline if area > 0 else outline[::-1]


def rounded_rect(u0, u1, y0, y1, r, per=4):
    """A rectangle's outline with rounded corners, counter-clockwise."""
    out = []
    for cx, cy, a0 in ((u1 - r, y0 + r, -90.0), (u1 - r, y1 - r, 0.0), (u0 + r, y1 - r, 90.0), (u0 + r, y0 + r, 180.0)):
        for i in range(per + 1):
            a = math.radians(a0 + 90.0 * i / per)
            out.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return out


# --- The parts --------------------------------------------------------------------------------------------

def hood(m):
    ys = [HOOD_END + 0.03, 2.72, 2.85, 3.0, 3.2, 3.45, 3.8, 4.2] + [4.2 + (12.9 - 4.2) * i / 15 for i in range(1, 16)] + \
         [13.15, 13.35, 13.5, 13.62, 13.7]
    rings = []
    for y in ys:
        hw, top = hood_section(y)
        rings.append(k.ring(y, max(hw, 0.05), 1.0, 36, z=0.0, top=max(top, 0.05), bottom=HOOD_UNDER * min(1.0, hw / 3.0 + 0.2),
                            power=HOOD_POWER))
    obj = k.loft("hood", rings, m["hood"], start_point=(0, HOOD_END, 0.0), end_point=(0, HOOD_TIP, 0.3))
    out = [k.smooth(obj, 45)]
    # The spine down its middle, a rounded ridge.
    y0, y1 = 1.6, 13.25
    rings = []
    for i in range(30):
        y = y0 + (y1 - y0) * i / 29
        f = end_round(y, y0, y1, 0.9, 0.8)
        rings.append(k.ring(y, SPINE_HALF * max(f, 0.15), 1.0, 14, z=hood_top(0.0, y) - 0.45,
                            top=0.45 + 0.5 * f, bottom=0.6, power=2.6))
    out.append(k.smooth(k.loft("spine", rings, m["spine"]), 50))
    # The grooves either side of the spine and across the flanks: dark lines sunk into the hood.
    for side in (-1, 1):
        line = [Vector((side * GROOVE_U, y, hood_top(side * GROOVE_U, y) - 0.08)) for y in
                [3.7 + (12.3 - 3.7) * i / 16 for i in range(17)]]
        out.append(tube(f"groove{side}", line, [0.2] * len(line), m["seam"], 8))
        us = [GROOVE_U + 0.2 + (6.9 - GROOVE_U - 0.2) * i / 10 for i in range(11)]
        line = [Vector((side * u, ACROSS_Y - 0.1 * (u - GROOVE_U), hood_top(side * u, ACROSS_Y) - 0.08)) for u in us]
        out.append(tube(f"across{side}", line, [0.2] * len(line), m["seam"], 8))
    return out


def gills(m):
    """The blue gills on the hood's lower flanks: a dark blue panel lying in the hood, a light ridge down
    its middle."""
    out = []
    u0, u1, y0, y1 = GILL
    outline = rounded_rect(-u1, -u0, y0, y1, 0.6)
    panel = surface_pad("gill_l", outline, hood_top, m["blue_dark"], lift=0.08, sink=0.5, dome=0.04)
    out += [panel, mirrored(panel)]
    um = -0.5 * (u0 + u1) - 0.1
    ridge = [Vector((um + 0.15 * (y - y0) / (y1 - y0), y, hood_top(um, y) + 0.05)) for y in
             [y0 + 0.35 + (y1 - y0 - 0.7) * i / 8 for i in range(9)]]
    r = tube("gill_ridge_l", ridge, [0.32] * len(ridge), m["blue_light"], 8, squash=0.7)
    out += [r, mirrored(r)]
    return out


def wing(m):
    """The thin blue blade across (row 11), pointed at both ends, drooping a little towards them."""
    us = [0.0, 1.5, 3.0, 4.5, 6.0, 7.2, 8.3, 9.1, 9.7, 10.2, 10.6, 10.9, 11.08]
    rings = []
    for u in us:
        s = u / WING_SPAN
        chord = 2.4 * max(min(1.0, (WING_SPAN - u) / 2.0) ** 0.8, 0.05)
        th = 0.38 * (1 - 0.45 * s) * max(min(1.0, (WING_SPAN - u) / 1.2) ** 0.5, 0.3)
        z = WING_Z - 0.45 * s ** 2
        y = WING_Y
        ring = []
        for j in range(14):
            a = 2 * math.pi * j / 14
            c, sn = math.cos(a), math.sin(a)
            ring.append(Vector((-u, y + 0.5 * chord * math.copysign(abs(c) ** 0.75, c), z + th * sn)))
        rings.append(ring)
    left = k.loft("wing_l", rings, m["blue"], cap_start=False, end_point=(-WING_SPAN, WING_Y, WING_Z - 0.45))
    k.smooth(left, 55)
    return [left, mirrored(left, 55)]


def jaw(m):
    """The grey bracket under the blade (rows 12-14): a bar across (columns 9-14) and two prongs down either
    side of the crystal's top (columns 8-10 and 14-16), rounded plates (polish_redjet.facet)."""
    flat = lambda u, y: -0.35  # noqa: E731
    bar = rounded_rect(-2.9, 2.9, 0.4, 2.55, 0.9)
    out = [facet("jaw_bar", resample(bar, 0.42), flat, 2.35, m["spine"], rim=0.6, steps=3, dome=0.15, dome_rings=2,
                 sink=0.0)]
    prong = [(-4.55, 1.6), (-2.15, 1.6), (-1.75, 0.2), (-2.05, -0.95), (-3.0, -1.2), (-4.25, -0.75)]
    prong = resample(ccw(chaikin(prong, 2)), 0.42)
    left = facet("jaw_prong_l", prong, flat, 2.1, m["spine"], rim=0.55, steps=3, dome=0.12, dome_rings=2, sink=0.0)
    out += [left, mirrored(left)]
    return out


def crystal(m):
    """The blue crystal (rows 13-19): a diamond in plan, faceted, a light ridge down its middle."""
    y0, y1 = CRYSTAL_Y
    ys = [y0 + (y1 - y0) * i / 16 for i in range(1, 16)]
    rings = []
    for y in ys:
        hw, ridge = CRYSTAL(y)
        hw = max(hw, 0.05)
        # The section: a low edge, two facets either side rising to the ridge, a flat underside.
        pts = [(hw, -0.3), (hw * 0.98, 0.25), (hw * 0.55, ridge * 0.72), (0.0, ridge), (-hw * 0.55, ridge * 0.72),
               (-hw * 0.98, 0.25), (-hw, -0.3), (-hw * 0.5, -0.45), (hw * 0.5, -0.45)]
        rings.append([Vector((x, y, z)) for x, z in pts])
    obj = k.loft("crystal", rings, m["crystal"], start_point=(0, y0, 0.6), end_point=(0, y1, 1.4))
    k.smooth(obj, 20)
    # Its light ridge.
    line = [Vector((0.0, y, CRYSTAL(y)[1] + 0.02)) for y in [y0 + 0.7 + (y1 - y0 - 1.6) * i / 12 for i in range(13)]]
    ridge = tube("crystal_ridge", line, [0.26] * len(line), m["blue_light"], 8, squash=0.6)
    return [obj, ridge]


def tendrils(m):
    """The two tendrils hanging from the blade: blue where they leave it, grey below row 17, their ends
    curling in towards the engine."""
    path = catmull(TENDRIL, 0.45)
    # Radii along the smoothed path, by the nearest control point's share.
    lengths = [0.0]
    for a, b in zip(path, path[1:]):
        lengths.append(lengths[-1] + (b - a).length)
    control = [0.0]
    for a, b in zip(TENDRIL, TENDRIL[1:]):
        control.append(control[-1] + (Vector(b) - Vector(a)).length)
    scale = lengths[-1] / control[-1]
    radii = []
    for d in lengths:
        c = d / scale
        i = max(0, min(len(control) - 2, next((j for j in range(len(control) - 1) if c <= control[j + 1]), len(control) - 2)))
        f = (c - control[i]) / max(control[i + 1] - control[i], 1e-6)
        radii.append(TENDRIL_RADII[i] + (TENDRIL_RADII[i + 1] - TENDRIL_RADII[i]) * f)
    obj = tube("tendril_l", path, radii, None, 10, squash=0.8)
    obj.data.materials.append(m["blue"])
    obj.data.materials.append(m["claw"])
    obj.data.materials.append(m["blue_light"])
    for poly in obj.data.polygons:
        c = poly.center
        if c.y < TENDRIL_GREY_Y:
            poly.material_index = 1
        elif c.x < -6.0 and poly.normal.x < -0.35 and poly.normal.z > 0.1 and c.y < 1.2:
            poly.material_index = 2  # the light outer edge of the blue part (the sprite's 3c, 3e)
    k.smooth(obj, 60)
    return [obj, mirrored(obj, 60)]


def engine(m):
    """The engine: a dark cowl (rows 20-22) with grey ribs along it, the outer two running on as guards
    beside the flame (rows 23-24), and the nozzle the flame comes out of."""
    out = []
    y0, y1 = COWL_Y
    ys = [y0, y0 + 0.08, y0 + 0.3] + [y0 + 0.3 + (y1 - 0.9 - y0 - 0.3) * i / 5 for i in range(1, 6)] + \
         [y1 - 0.5, y1 - 0.25, y1 - 0.08]
    rings = []
    for y in ys:
        f = end_round(y, y0, y1, 0.3, 0.9)
        rings.append(k.ring(y, COWL_HALF * (0.9 + 0.1 * f), 1.0, 36, z=ENGINE_Z, top=COWL_HEIGHT * (0.55 + 0.45 * f),
                            bottom=COWL_HEIGHT * (0.55 + 0.45 * f), power=2.8))
    cowl = k.loft("cowl", rings, m["engine"], start_point=(0, y0 - 0.02, ENGINE_Z), end_point=(0, y1 + 0.02, ENGINE_Z))
    out.append(k.smooth(cowl, 40))

    def cowl_top(u, y):
        f = end_round(y, y0, y1, 0.3, 0.9)
        hw, hh = COWL_HALF * (0.9 + 0.1 * f), COWL_HEIGHT * (0.55 + 0.45 * f)
        if abs(u) >= hw:
            return ENGINE_Z
        return ENGINE_Z + hh * (1 - (abs(u) / hw) ** 2.8) ** (1 / 2.8)

    # The ribs: raised rounded strips along the cowl.
    for i, u in enumerate(RIBS_U):
        line = [Vector((u, y, cowl_top(u, y) - 0.05)) for y in [y0 + 0.25 + (y1 - 0.45 - y0 - 0.25) * j / 8 for j in range(9)]]
        out.append(tube(f"rib{i}", line, [0.42] * len(line), m["claw"], 8, squash=0.8))
    # The guards: the outer ribs, from the cowl's top end down beside the flame (columns 8 and 16).
    for side in (-1, 1):
        pts = [Vector((side * GUARD_U, y1 - 0.35, ENGINE_Z + 1.2)), Vector((side * GUARD_U, y1 - 1.4, ENGINE_Z + 1.45)),
               Vector((side * (GUARD_U + 0.05), y0 + 0.2, ENGINE_Z + 1.3)), Vector((side * (GUARD_U - 0.05), y0 - 1.0, ENGINE_Z + 0.95)),
               Vector((side * (GUARD_U - 0.2), GUARD_END + 0.4, ENGINE_Z + 0.6))]
        path = catmull(pts, 0.3)
        radii = [0.62] * (len(path) - 3) + [0.58, 0.5, 0.4]
        out.append(tube(f"guard{side}", path, radii, m["claw"], 10, squash=1.0))
    # The nozzle: a dark ring at the cowl's lower end, the flame's root inside it.
    prof = [(NOZZLE_Y + 0.25, 2.55), (NOZZLE_Y - 0.15, 2.65), (NOZZLE_Y - 0.45, 2.45), (NOZZLE_Y - 0.5, 2.0),
            (NOZZLE_Y - 0.25, 1.6), (NOZZLE_Y + 0.1, 0.0)]
    rings = [k.ring(y, r, r * 0.72, 24, z=ENGINE_Z) for y, r in prof if r > 0]
    nozzle = k.loft("nozzle", rings[::-1], m["nozzle"], start_point=(0, NOZZLE_Y + 0.1, ENGINE_Z),
                    end_point=(0, NOZZLE_Y + 0.25, ENGINE_Z), cap_end=False)
    out.append(k.smooth(nozzle, 50))
    return out


FLAME_HEIGHT = 1.5      # the outer tongue's half-height at its widest (the core's stays inside the ship's height)


def flame(spec, mats):
    """The engine's fire along -y from the nozzle, in three layers (FLAME_LAYERS): the outer tongue (the
    frame's outline), a brighter one inside it and a hot core (smooth tongues, widest near the root), each a
    little taller than the one round it so that it shows on top, as the sprite's fire is brightest in its
    middle."""
    out = []
    outline = Curve([(d, w) for d, w in spec])
    length = spec[-1][0]
    wmax = max(w for _, w in spec)
    for name, reach, wide, tall in FLAME_LAYERS:
        end = length * reach
        rings = []
        count = 14
        for i in range(count + 1):
            d = end * (0.02 + 0.98 * i / count)
            if reach < 1:
                t = d / end
                w = wide * wmax * min(1.0, 0.75 + 1.2 * t) * (1 - t ** 2.2) ** 0.55
            else:
                w = outline(d)
            w = max(w, 0.04)
            h = min(FLAME_HEIGHT, 0.62 * wmax) * tall * (w / (wmax * wide)) ** 0.55
            y = FLAME_ROOT - d
            ring = []
            for j in range(16):
                a = 2 * math.pi * j / 16
                c, s = math.cos(a), math.sin(a)
                ring.append(Vector((math.copysign(abs(c) ** 0.85, c) * w, y, FLAME_Z + s * h)))
            rings.append(ring)
        obj = k.loft(name, rings, mats[name], start_point=(0, NOZZLE_Y + 0.1, FLAME_Z),
                     end_point=(0, FLAME_ROOT - end - 0.03, FLAME_Z))
        out.append(k.smooth(obj, 60))
    return out


# --- Build ----------------------------------------------------------------------------------------------

def materials(colours):
    pal = k.level_palette()
    m = {
        "hood": k.material("squid_hood", palette=7, metallic=0.35, roughness=0.3),
        "spine": k.material("squid_spine", palette=7, metallic=0.4, roughness=0.3),
        "seam": k.material("squid_seam", palette=1, metallic=0.3, roughness=0.55),
        "blue": k.material("squid_blue", palette=0x38, metallic=0.35, roughness=0.22, emission=pal[0x37],
                           emission_strength=0.25),
        "blue_dark": k.material("squid_blue_dark", palette=0x36, metallic=0.3, roughness=0.18, emission=pal[0x36],
                                emission_strength=0.25),
        "blue_light": k.material("squid_blue_light", palette=0x3c, metallic=0.3, roughness=0.2, emission=pal[0x3b],
                                 emission_strength=0.35),
        "crystal": k.material("squid_crystal", palette=0x38, metallic=0.25, roughness=0.1, emission=pal[0x37],
                              emission_strength=0.35),
        "claw": k.material("squid_claw", palette=9, metallic=0.45, roughness=0.3),  # the tendrils' ends, the ribs
        "engine": k.material("squid_engine", palette=3, metallic=0.4, roughness=0.4),
        "nozzle": k.material("squid_nozzle", palette=2, metallic=0.3, roughness=0.5),
    }
    for key, (index, strength) in colours.items():  # fire: no gloss, glowing in its own colour
        m[key] = k.material(f"squid_{key}_{index:x}", palette=index, roughness=0.85, emission=pal[index],
                            emission_strength=strength)
    return m


def build_model(spec, colours):
    k.reset()
    m = materials(colours)
    hood(m)
    gills(m)
    wing(m)
    jaw(m)
    crystal(m)
    tendrils(m)
    engine(m)
    flame(spec, m)
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


def bounds():
    vs = [obj.matrix_world @ v.co for obj in bpy.context.scene.objects if obj.type == "MESH" for v in obj.data.vertices]
    return [min(v[i] for v in vs) for i in range(3)], [max(v[i] for v in vs) for i in range(3)]


def build():
    options = k.args()
    outdir = options.get("outdir", os.path.join(HERE, "..", "..", "..", "..", "assets", "models", "enemies"))
    only = options["only"].split(",") if "only" in options else None
    for name, sprite, spec, colours in FRAMES:
        if only and name not in only:
            continue
        build_model(spec, colours)
        used = {mat.name for o in bpy.context.scene.objects if o.type == "MESH" for mat in o.data.materials}
        low, high = bounds()
        print("== %s (7 %d): %d triangles, %d materials, x %.2f to %.2f, y %.2f to %.2f, z %.2f to %.2f: %s" % (
            name, sprite, triangles(), len(used), low[0], high[0], low[1], high[1], low[2], high[2], ", ".join(sorted(used))))
        if "check" in options:
            sheet = options["check"]
            k.check_silhouette(os.path.join(sheet, "enemy_7.png") if os.path.isdir(sheet) else sheet, sprite)
        bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
        path = os.path.join(outdir, name + ".glb")
        k.export(path)
        print("%s: %.1f KB" % (path, os.path.getsize(path) / 1024))
        if "preview" in options:
            k.preview(options["preview"] + name)


if __name__ == "__main__":
    build()
