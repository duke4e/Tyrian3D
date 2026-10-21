"""MARKERS' steel-blue ship with the orange chevron (sheet V sprite 159, 2x2: 24 x 25 pixels in the 24 x 28 cell; episode
2's enemy 811, in the sky, drifting down the screen two pixels a tick; one frame, not animated) and the steel canister
it drops (V 171, 1x1: 10 x 6 pixels in the 12 x 14 cell; enemy 812, which 811 launches every 30 ticks from its middle on
its own layer, falling straight down the screen three pixels a tick), polished (2026-10-21; the ship replaces
wave3_t_ships.py's chevron_ship(), a hull inflated from the sprite's pixels with tubes for the band; the canister had no
model, the game drew it as a pixelated stand-in). models.cfg: sprite v 159 chevron_ship yaw=0 (unchanged); new: model
steel_canister enemies/steel_canister.glb, sprite v 171 steel_canister yaw=0.

MARKERS' events make the ship at 1440-2310 (x 30-220, links 1-16; one frame, no damaged look). No other enemy shows
V 171. TIME WAR's enemy 674 shows V 159 as two of its frames (155 157 159 159 159 157 ...: TIME WAR's sheet V picture
sequence), under its own rule (sprite v 155 facet_orb): so no frame line names V 159. No other sprite of any sheet is
V 159's or V 171's pixels mirrored, turned or in other ramps.

As the sprite and its 4x upscale draw the ship (columns and rows of the 24 x 28 cell; symmetric about the line between
columns 11 and 12, x 0): a hood of steel-blue armour (ramp 3) whose top (rows 3-16) rises to a crest along an orange band
like an inverted V: from the top middle (rows 4-5, between two rounded lobes, columns 8-10 and 13-15 of row 3) its legs
run down and out to the hood's sides (columns 4 and 19 of row 16), three pixels wide, red at their edges (0x72, 0x73),
yellow-orange along the middle (0x79-0x7b). Outside the band the shoulders fall away to the hood's edge, brightest next
to the band; inside it a slightly lower face holds a blue gem (columns 10-13 of rows 9-12, ramp 9, lit at its upper
left) and a light ridge down its middle (rows 13-17) to the mouth: an almond-shaped dark opening (rows 18-26, columns
7-16, pointed at its top) with a pale onion-shaped nose in it (columns 8-15 of rows 19-26, lit left of its middle). The
lower hull round the mouth narrows to the rounded bottom (row 27); either side of it, past a dark groove (columns 4 and
19 of rows 16-24), a curved blade like a mandible hangs from the hull (columns 0-3 of rows 17-26: its top tip at row 17,
bulging out to the cell's edge at rows 21-24, its lower end curling in at row 26), lit along its inner edge.

Built from lofts (tyrkit) as the upscale paints it: the hull one loft along y whose sections follow the sprite's
outline (the lobes' notch a dip at the top), their tops a crest along the band (falling away outside it, a lower face
inside, a gentle dome below it) and rounded sides; the band a strip laid along the crest (its sections rounded across,
red at the edges, yellow-orange along the middle, glowing a little in its own colours); the gem a painted ball in a
dark bezel (polish_balls, the green beetle's gem_paint and torus); the ridge and two light ridges diverging from under
the gem to the mouth's sides thin bars (polish_green_beetle.thin_tube); the mouth a dark plate laid into the face
(polish_redjet.facet) under a raised rim, the nose an onion-shaped loft lying in it, pale steel glowing very faintly (so
that it reads pale from the slanted camera, as the upscale paints it), a light streak along its upper left; the blades
tapering horns along their curves (polish_twin_claw.horn). The left blade is built and mirrored.

The canister as V 171 draws it (columns and rows of its 12 x 14 cell): a short drum lying across the screen (columns
1-10 of rows 3-8), lit along its top (row 5) and brightest in its middle (column 6), two dark grooves (columns 3 and 8)
between the middle and its end bands (columns 2 and 9), its ends rounded (columns 1 and 10). Built as one profile
turned about its axis (along x at y 1.0), polished steel; a sky object, centred in height by the game.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera; origin at the
sprite's centre (pixel 12, 14 of the ship's cell, pixel 6, 7 of the canister's): column c is x = c + 0.5 - 12 (- 6),
row r is y = 13.5 - r (6.5 - r). Both fly: the game centres them in height.

Replaces wave3_t_ships.py's chevron_ship() (its "# --- V 159: the steel ship with the orange chevron" section with the
@model("chevron_ship", [159]) registration, and the docstring's chevron_ship lines) and wave3_t_art.py's SPEAR (only
chevron_ship() reads it): remove them so that they don't overwrite this model.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouettes against
enemy_V.png sprites 159 and 171), --preview <prefix>, --only <name,...>, --stats 1.
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
import polish_machine_kit as mk  # noqa: E402
from polish_balls import Ellipsoid, painted_ball  # noqa: E402
from polish_green_beetle import gem_paint, thin_tube, torus  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402
from polish_redjet import Curve, chaikin, facet, resample, smoothstep  # noqa: E402
from polish_twin_claw import horn, paint_sections  # noqa: E402

NAMES = ("chevron_ship", "steel_canister")

# --- The ship's hull -------------------------------------------------------------------------------------------------
# Its plan: the half-width by y (pixel edges, through the middles of the sprite's steps; the blades are parts of their
# own), the height of its sides and of its underside.
PLAN = Curve([(-14.05, 0.4, 2.3, 1.9), (-13.9, 2.4, 2.3, 1.7), (-13.5, 3.9, 2.4, 1.5), (-12.9, 4.9, 2.5, 1.4),
              (-12.1, 5.8, 2.6, 1.3), (-11.3, 6.6, 2.7, 1.3), (-10.4, 7.3, 2.8, 1.3), (-9.2, 7.75, 2.9, 1.3),
              (-7.0, 7.9, 3.0, 1.3), (-4.6, 7.85, 3.05, 1.3), (-3.6, 7.6, 3.1, 1.3), (-2.9, 8.1, 3.2, 1.3),
              (-2.2, 8.75, 3.3, 1.3), (-1.0, 9.05, 3.4, 1.3), (1.5, 9.05, 3.5, 1.3), (3.5, 8.85, 3.6, 1.35),
              (5.0, 8.35, 3.6, 1.4), (6.5, 7.75, 3.6, 1.5), (7.8, 7.05, 3.5, 1.6), (8.9, 6.25, 3.4, 1.8),
              (9.8, 5.3, 3.3, 2.0), (10.5, 4.3, 3.1, 2.2), (10.9, 3.3, 2.9, 2.4), (11.1, 2.0, 2.7, 2.5)])
HULL_Y = (-14.05, 11.1)
SIDE_POWER = (2.6, 2.0)     # the sections' superellipse powers: top, underside
# The band's middle line (its left leg; the right is its mirror image): |x| by y, from the apex down to its end at the
# hood's side; beyond its end the line runs on off the hull so that the face's edge leaves it smoothly.
BAND_X = Curve([(-4.4, 11.5), (-3.4, 9.0), (-2.65, 7.55), (-1.5, 6.35), (-0.5, 5.35), (0.5, 4.65), (1.5, 4.5),
                (2.5, 4.35), (3.5, 3.95), (4.5, 3.35), (5.5, 2.7), (6.5, 2.3), (7.5, 1.5), (8.5, 0.65), (9.4, 0.0)])
BAND_END = -2.65
# The crest's height along the band by y; the face's height in the middle by y (lower than the crest).
CREST_Z = Curve([(-14.0, 3.0), (-6.0, 4.0), (-3.5, 4.8), (-2.6, 5.25), (-1.0, 5.95), (1.0, 6.6), (3.0, 7.15),
                 (5.0, 7.5), (7.0, 7.7), (9.0, 7.65), (10.0, 7.3), (11.2, 6.4)])
FACE_Z = Curve([(-14.0, 2.9), (-12.5, 3.55), (-10.0, 4.3), (-7.0, 4.9), (-4.0, 5.4), (-2.0, 5.65), (0.0, 5.9),
                (2.0, 6.15), (4.0, 6.3), (6.0, 6.3), (8.0, 6.1), (9.3, 5.8)])
SHOULDER_FALL = 0.2         # the shoulders fall this much per pixel squared outside the band
FACE_FALL = 0.018           # the face's dome across
NOTCH = (0.85, 9.7, 10.7)   # the lobes' notch: its half-width, where it starts and is full depth (y)

# The band: its width, how high it stands over the crest, the share of each edge in red.
BAND_W, BAND_H = 2.7, 0.62
# The gem (columns 10-13 of rows 9-12) and its bezel.
GEM = Ellipsoid((0.0, 3.05, 0.0), (1.85, 2.15, 1.2))
GEM_BEZEL = (2.15, 0.42)
# The ridge down the face (rows 13-17) and the two light ridges either side of it, from under the gem down to the
# mouth's rim (columns 8-9 and 14-15 of rows 14-17).
RIDGE = [(0.0, 0.55), (0.0, -1.5), (0.0, -3.0), (0.0, -3.9)]
SIDE_RIDGE = [(-0.95, 0.45), (-1.9, -1.7), (-3.0, -4.1), (-3.95, -6.6)]
# The mouth (rows 18-26): its outline (pixel edges round the dark ring), the nose in it: its middle line (y, radius)
# from its point to its round end, its middle (x, z over the face).
MOUTH = [(0.0, -4.05), (-1.4, -5.05), (-2.75, -6.3), (-3.95, -7.45), (-4.7, -8.9), (-4.75, -10.4), (-4.2, -11.7),
         (-3.0, -12.65), (-1.2, -13.05), (1.2, -13.05), (3.0, -12.65), (4.2, -11.7), (4.75, -10.4), (4.7, -8.9),
         (3.95, -7.45), (2.75, -6.3), (1.4, -5.05)]
NOSE = [(-5.2, 0.05), (-5.6, 0.5), (-6.5, 1.15), (-7.5, 1.95), (-8.4, 2.6), (-9.4, 2.9), (-10.5, 2.95),
        (-11.4, 2.7), (-12.1, 2.15), (-12.55, 1.3), (-12.75, 0.05)]
NOSE_X, NOSE_SQUASH, NOSE_SINK = -0.15, 0.7, 0.45
# The left blade: (x, y, z, half-width in plan, half-height) from its lower end to its top tip.
BLADE = [(-8.0, -12.85, 2.0, 0.25, 0.22), (-9.0, -12.4, 2.1, 0.85, 0.6), (-9.85, -11.4, 2.25, 1.4, 0.85),
         (-10.2, -9.9, 2.4, 1.85, 1.0), (-10.15, -8.0, 2.55, 1.95, 1.05), (-9.85, -6.3, 2.7, 1.7, 0.98),
         (-9.4, -4.9, 2.8, 1.25, 0.8), (-8.85, -3.85, 2.85, 0.75, 0.52), (-8.45, -3.25, 2.85, 0.25, 0.22)]

# --- The canister ----------------------------------------------------------------------------------------------------
CAN_AXIS = (1.0, 3.0)       # y, z of its axis (rows 3-8: radius 3)
# Its profile along x (the right half; mirrored): (x, radius).
CAN = [(0.0, 3.0), (1.95, 3.0), (2.12, 2.9), (2.3, 2.74), (2.62, 2.74), (2.8, 2.9), (2.95, 2.97), (3.9, 2.97),
       (4.2, 2.86), (4.5, 2.6), (4.75, 2.2), (4.92, 1.65), (5.0, 1.0), (5.03, 0.0)]
CAN_GROOVE = (2.08, 2.84)
CAN_END = 4.3


def materials():
    pal = k.level_palette()

    def steel(name, index, metallic=0.55, roughness=0.26):
        return k.material(name, palette=index, metallic=metallic, roughness=roughness)

    def lit(name, index, strength, roughness=0.2, metallic=0.25, glow=None):
        return k.material(name, palette=index, metallic=metallic, roughness=roughness, emission=pal[glow or index],
                          emission_strength=strength)
    return {
        "shoulder": steel("chv_shoulder", 0x3c, 0.55, 0.22),
        "face": steel("chv_face", 0x3b, 0.55, 0.25),
        "blade": steel("chv_blade", 0x3a, 0.55, 0.25),
        "dark": steel("chv_dark", 0x34, 0.45, 0.4),
        "deep": steel("chv_deep", 0x32, 0.3, 0.55),
        "band_red": lit("chv_band_red", 0x74, 0.2, glow=0x76),
        "band": lit("chv_band", 0x79, 0.3),
        "band_hot": lit("chv_band_hot", 0x7b, 0.4),
        "gem_rim": lit("chv_gem_rim", 0x93, 0.15, 0.12, 0.1),
        "gem": lit("chv_gem", 0x96, 0.22, 0.12, 0.1),
        "gem_light": lit("chv_gem_light", 0x9a, 0.38, 0.12, 0.1),
        "gem_core": lit("chv_gem_core", 0x9d, 0.5, 0.12, 0.1),
        "nose": lit("chv_nose", 0x3c, 0.06, 0.14, 0.35, glow=0x3d),
        "nose_light": lit("chv_nose_light", 0x3e, 0.1, 0.1, 0.3),
    }


# --- The hull's surface ----------------------------------------------------------------------------------------------

def band_x(y):
    return BAND_X(y)


def top_z(x, y):
    """The hull's top at (x, y): a crest along the band falling away outside it, a lower face inside, a gentle dome
    below it; the lobes' notch at the top middle."""
    u = abs(x)
    xb = band_x(y)
    crest = CREST_Z(y)
    shoulder = crest - SHOULDER_FALL * (u - xb) ** 2 if y > BAND_END - 1.6 else -99.0
    if y > BAND_END - 1.6:
        shoulder -= 2.5 * smoothstep(BAND_END, BAND_END - 1.6, y)
    face = FACE_Z(min(y, 9.3)) - FACE_FALL * u * u - 1.6 * max(0.0, u - xb + 0.35) ** 2
    if y > 8.6:
        face -= 3.0 * smoothstep(8.6, 9.6, y)
    z = max(shoulder, face)
    w, y0, y1 = NOTCH
    z -= (z - 2.4) * math.exp(-(x / w) ** 2) * smoothstep(y0, y1, y)
    return z


def hull(m, segments=48, count=40):
    rings = []
    for i in range(count + 1):
        t = i / count
        y = HULL_Y[0] + (HULL_Y[1] - HULL_Y[0]) * (0.5 - 0.5 * math.cos(math.pi * t))
        hw, zc, zb = PLAN(y)
        pts = []
        for j in range(segments):
            a = 2 * math.pi * j / segments
            c, s = math.cos(a), math.sin(a)
            p = SIDE_POWER[0] if s >= 0 else SIDE_POWER[1]
            u = math.copysign(abs(c) ** (2 / p), c)
            v = math.copysign(abs(s) ** (2 / p), s)
            x = hw * u
            if s >= 0:
                z = zc + (max(top_z(x, y), zc + 0.2) - zc) * v
            else:
                z = zc + (zc - zb) * v
            pts.append(Vector((x, y, z)))
        rings.append(pts)
    y0, y1 = HULL_Y
    obj = k.loft("hull", rings[1:-1], m["shoulder"], start_point=(0.0, y0, PLAN(y0)[2] + 0.3),
                 end_point=(0.0, y1, PLAN(y1)[1] + 0.4))
    k.smooth(obj, 50)

    def pick(c, n):
        if n.z < 0.15:
            return m["dark"]
        if n.z < 0.45:
            return m["blade"]
        if abs(c.x) < band_x(c.y) - 0.9 or c.y < BAND_END - 0.8:
            return m["face"]
        return None
    mk.paint(obj, pick)
    return obj


# --- The band ----------------------------------------------------------------------------------------------------------

def band_path():
    """The band's middle line from its left end over the apex to its right end, resampled evenly."""
    ys = [BAND_END + 0.1 + (9.25 - BAND_END - 0.1) * i / 40 for i in range(41)]
    left = [(-band_x(y), y) for y in ys]
    apex = [(0.0, 9.55)]
    pts = left + apex + [(-x, y) for x, y in reversed(left)]
    pts = chaikin_open(pts, 3)
    return resample_open(pts, 0.42)


def chaikin_open(points, iterations):
    pts = [tuple(p) for p in points]
    for _ in range(iterations):
        out = [pts[0]]
        for i in range(len(pts) - 1):
            p, q = pts[i], pts[i + 1]
            out.append((0.75 * p[0] + 0.25 * q[0], 0.75 * p[1] + 0.25 * q[1]))
            out.append((0.25 * p[0] + 0.75 * q[0], 0.25 * p[1] + 0.75 * q[1]))
        out.append(pts[-1])
        pts = out
    return pts


def resample_open(points, spacing):
    lengths = [math.dist(points[i], points[i + 1]) for i in range(len(points) - 1)]
    total = sum(lengths)
    count = max(2, int(round(total / spacing)))
    out, i, walked = [], 0, 0.0
    for c in range(count + 1):
        target = total * c / count
        while i < len(lengths) - 1 and walked + lengths[i] < target:
            walked += lengths[i]
            i += 1
        t = (target - walked) / lengths[i] if lengths[i] > 0 else 0.0
        p, q = points[i], points[i + 1]
        out.append((p[0] + (q[0] - p[0]) * min(1.0, t), p[1] + (q[1] - p[1]) * min(1.0, t)))
    return out


def band(m, surface):
    """A strip along the band's line, its sections rounded across (BAND_W wide, standing BAND_H over the surface),
    tapering at its ends into the hull; painted red along its edges, yellow-orange along its middle."""
    path = band_path()
    across = 8
    rings, keys = [], []
    n = len(path)
    for i, (px, py) in enumerate(path):
        a, b = path[max(i - 1, 0)], path[min(i + 1, n - 1)]
        t = Vector((b[0] - a[0], b[1] - a[1], 0.0)).normalized()
        side = Vector((-t.y, t.x, 0.0))
        end = min(i, n - 1 - i) / 4.0
        taper = math.sqrt(min(1.0, end)) if end < 1.0 else 1.0
        half = BAND_W / 2 * (0.55 + 0.45 * taper)
        ring = []
        for j in range(across + 1):
            u = -1.0 + 2.0 * j / across
            q = Vector((px, py, 0.0)) + side * (u * half)
            hit = surface(q.x, q.y)
            z0 = hit[0].z if hit else 3.0
            ring.append(Vector((q.x, q.y, z0 - 0.15 + (BAND_H * taper + 0.15) * (1 - abs(u) ** 2.4) ** (1 / 2.4))))
        for j in range(across - 1, 0, -1):
            u = -1.0 + 2.0 * j / across
            q = Vector((px, py, 0.0)) + side * (u * half * 0.92)
            hit = surface(q.x, q.y)
            z0 = hit[0].z if hit else 3.0
            ring.append(Vector((q.x, q.y, z0 - 0.7)))
        rings.append(ring)
    first, last = path[0], path[-1]
    h0, h1 = surface(*first), surface(*last)
    obj = k.loft("band", rings, m["band"], start_point=(first[0], first[1], (h0[0].z if h0 else 3.0) - 0.2),
                 end_point=(last[0], last[1], (h1[0].z if h1 else 3.0) - 0.2))
    k.smooth(obj, 60)
    # Paint by where across the strip each face lies (its first vertex's index in the ring).
    per = len(rings[0])
    slots = {key: mk.slot_of(obj, m[key]) for key in ("band", "band_red", "band_hot")}
    for poly in obj.data.polygons:
        j = min(v % per for v in poly.vertices if v < per * len(rings)) if any(v < per * len(rings)
                                                                               for v in poly.vertices) else 0
        if j >= across:
            continue
        u = -1.0 + 2.0 * (j + 0.5) / across
        if u > 0.62 or u < -0.75:
            poly.material_index = slots["band_red"]
        elif -0.3 < u < 0.05:
            poly.material_index = slots["band_hot"]
        else:
            poly.material_index = slots["band"]
    return obj


# --- The face's details ------------------------------------------------------------------------------------------------

def gem(m, surface):
    hit = surface(GEM.centre.x, GEM.centre.y)
    z = (hit[0].z if hit else 6.5) - 0.25
    mats = {"rim": m["gem_rim"], "body": m["gem"], "light": m["gem_light"], "core": m["gem_core"]}
    shape = Ellipsoid((GEM.centre.x, GEM.centre.y, z), GEM.radii)
    ball = painted_ball("gem", shape, gem_paint((-0.55, 3.6), (0.9, 1.0), 0.75, (-0.7, 3.9), (0.4, 0.45)), mats,
                        subdivisions=3, smooth_angle=80)
    radius, thick = GEM_BEZEL
    bezel = torus("gem_bezel", (GEM.centre.x, GEM.centre.y, z + 0.1), radius, thick, m["dark"],
                  scale=(GEM.radii.x + 0.3, GEM.radii.y + 0.3))
    return [ball, bezel]


def ridge(m, surface):
    def on(points, sink):
        out = []
        for x, y in points:
            hit = surface(x, y)
            out.append(Vector((x, y, (hit[0].z if hit else 6.0) - sink)))
        return out
    parts = [thin_tube("ridge", on(RIDGE, 0.1), 0.42, m["nose"], 8, squash=0.8)]
    parts.append(thin_tube("side_ridge_l", on(SIDE_RIDGE, 0.12), 0.36, m["shoulder"], 6, squash=0.8))
    parts.append(thin_tube("side_ridge_r", on([(-x, y) for x, y in SIDE_RIDGE], 0.12), 0.36, m["shoulder"], 6,
                           squash=0.8))
    return parts


def mouth(m, surface):
    def base(x, y):
        hit = surface(x, y)
        return (hit[0].z if hit else 4.5) - 0.3
    outline = resample(chaikin(MOUTH, 1), 0.4)
    area = sum(outline[i][0] * outline[(i + 1) % len(outline)][1] - outline[(i + 1) % len(outline)][0] *
               outline[i][1] for i in range(len(outline)))
    if area < 0:
        outline = outline[::-1]
    plate = facet("mouth", outline, base, 0.38, m["deep"], rim=0.15, steps=2, dome=0.0, dome_rings=1, sink=0.5)
    rim_pts = []
    for x, y in resample(chaikin(MOUTH, 1), 0.5):
        cx, cy = 0.0, -8.6
        d = math.hypot(x - cx, y - cy)
        f = (d + 0.35) / d
        rx, ry = cx + (x - cx) * f, cy + (y - cy) * f
        hit = surface(rx, ry)
        rim_pts.append(Vector((rx, ry, (hit[0].z if hit else 4.5) - 0.05)))
    rim_pts.append(rim_pts[0])
    rim = thin_tube("mouth_rim", rim_pts, 0.5, m["shoulder"], 6, squash=0.75, iterations=0)
    # The nose: an onion lying in the mouth, its point up the screen.
    rings = []
    hz = base(NOSE_X, -9.0) + 0.3 - NOSE_SINK
    for y, r in NOSE[1:-1]:
        rings.append(k.ring(y, r, r * NOSE_SQUASH, 28, z=hz, x=NOSE_X))
    obj = k.loft("nose", rings, m["nose"], start_point=(NOSE_X, NOSE[0][0], hz),
                 end_point=(NOSE_X, NOSE[-1][0], hz))
    k.smooth(obj, 60)
    mk.paint(obj, lambda c, n: m["nose_light"] if n.z > 0.62 and -0.62 < n.x < -0.18 and c.y < -6.6 else
             m["face"] if n.z < 0.2 else None)
    return [plate, rim, obj]


def blades(m):
    obj, centres = horn("blade_l", BLADE, m["blade"], 10)
    paint_sections(obj, centres, 10, lambda c, n: m["dark"] if n.z < 0.1 else
                   m["nose"] if n.z > 0.45 and n.x > 0.15 else None)
    return [obj]


def mirrored(objects):
    out = []
    for obj in objects:
        copy = obj.copy()
        copy.data = obj.data.copy()
        copy.name = obj.name[:-2] + "_r" if obj.name.endswith("_l") else obj.name + "_r"
        bpy.context.scene.collection.objects.link(copy)
        copy.data.transform(Matrix.Scale(-1, 4, (1, 0, 0)))
        copy.data.flip_normals()
        out.append(copy)
    return out


def ship():
    m = materials()
    body = hull(m)
    bpy.context.view_layer.update()
    surface = mk.surface([body])
    parts = [body, band(m, surface)] + gem(m, surface) + ridge(m, surface) + mouth(m, surface)
    left = blades(m)
    return parts + left + mirrored(left)


# --- The canister --------------------------------------------------------------------------------------------------------

def canister():
    m = materials()
    y0, z0 = CAN_AXIS
    profile = [(-x, r) for x, r in reversed(CAN[1:])] + CAN
    segments = 36
    rings = [[Vector((x, y0 + r * math.cos(2 * math.pi * j / segments), z0 + r * math.sin(2 * math.pi * j / segments)))
              for j in range(segments)] for x, r in profile if r > 1e-6]
    obj = k.loft("canister", rings, m["shoulder"], start_point=(profile[0][0], y0, z0),
                 end_point=(profile[-1][0], y0, z0))
    k.smooth(obj, 45)
    g0, g1 = CAN_GROOVE

    def pick(c, n):
        ax = abs(c.x)
        if g0 <= ax <= g1:
            return m["dark"]
        if ax > CAN_END:
            return m["blade"]
        return None
    mk.paint(obj, pick)
    return [obj]


# --- Building --------------------------------------------------------------------------------------------------------------

def build():
    options = k.args()
    out = mk.outdir(options)
    only = set(options["only"].split(",")) if "only" in options else None
    for name in NAMES:
        if only and name not in only:
            continue
        k.reset()
        parts = ship() if name == "chevron_ship" else canister()
        triangulate(parts)
        bpy.context.view_layer.update()
        if "stats" in options:
            for obj in parts:
                print("  %-16s %5d triangles" % (obj.name, len(obj.data.polygons)))
        size = (24, 28) if name == "chevron_ship" else (12, 14)
        if "check" in options:
            sheet = os.path.join(options["check"], "enemy_V.png")
            sprite = 159 if name == "chevron_ship" else 171
            mk.compare("%s (V %d)" % (name, sprite), mk.coverage(parts, *size),
                       k.sprite_mask(sheet, sprite, name == "chevron_ship"))
        bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
        mk.report(name, parts, os.path.join(out, name + ".glb"))
        if "preview" in options:
            mk.preview(options["preview"] + name, parts, size=size, distance=0.7 if size[0] == 24 else 0.45)


if __name__ == "__main__":
    build()
