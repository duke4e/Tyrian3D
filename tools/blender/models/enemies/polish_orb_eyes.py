"""The black orb with two glowing eyes of BUBBLES, BONUS, MISTAKES, STARGATE, FLEET, LAVA EXIT, ASTEROIDS
and COLLECTOR (sheet E sprite 195, 2x2: a 21 x 21 orb in the 24 x 28 cell; ground, sky and top
layers), polished (2026-10-18; it replaces later_episodes.py's plain dark sphere with two lights).
models.cfg: sprite e 195 orb_eyes yaw=0.

As the 4x upscale draws it: a glossy orb of dark red glass (the sprite's ramp 7) under a black hood
that covers its upper middle (columns 5-19 of rows 5-13, narrowing to a blunt point at column 13 of
row 18), its edge raised a little over the red, which lies round it in folds (a lighter roll, then
a dark crease). Two eyes glow in the hood: the left one bigger, white-hot in the middle through
yellow and orange (columns 7-10 of rows 9-12), the right one smaller, red-orange (columns 13-15 of
rows 9-11), each a soft lens. Molten orange seeps out round the orb's lower rim, along a sunken
seam: warm on the lower left, red-orange round the bottom and white-hot at the lower right (column
18 of row 21), as the sprite's ramp 7 runs up to 0x7f there.

The face (the hood and the eyes) sits FACE_SHIFT (2 pixels) lower on the orb than the sprite draws
it: the game's camera, slanted 20 degrees, sees the orb a little from the bottom of the screen and
shows the face, high on the orb, where the sprite does (as polish_blocks.py moves its emblems).

Built as polish_orb_red.py builds its orb: an ellipsoid of even triangles painted in bands of heat
(band_split), the hotter bands glowing in their own colour.

Origin at the sprite's centre (pixel 12, 14); +Y up the sprite, +Z towards the camera.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <enemy_E.png or the
directory of the exported sheets> (the silhouette), --preview <prefix>.
"""
import math
import os
import sys

import bmesh
import bpy
import mathutils.noise as noise
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import tyrkit as k  # noqa: E402
from polish_orb_red import band_split, smoothstep  # noqa: E402

CENTRE = Vector((0.5, -0.5, 0.0))   # the sprite's columns 2-22, rows 4-24
RADII = Vector((10.45, 10.45, 9.6))

# The face (the hood and the eyes, given below as the sprite draws them) is moved down the screen by
# FACE_SHIFT: the game's slanted camera (20 degrees) shows it on the orb where the sprite does (seen
# straight from above it sits lower than in the sprite).
FACE_SHIFT = 2.0

# The hood: its outline in the top view, as distances from HOOD_MIDDLE at angles round it (degrees,
# counter-clockwise from the right), how much it is raised over the red and the width of its edge.
HOOD_MIDDLE = (0.5, 2.0)
HOOD_OUTLINE = [(0, 7.0), (30, 6.8), (60, 6.5), (90, 6.8), (120, 7.1), (150, 7.3), (180, 7.0), (210, 5.9),
                (240, 5.4), (265, 6.0), (283, 6.6), (300, 5.9), (325, 5.0), (348, 5.8)]
HOOD_RAISE, HOOD_EDGE, HOOD_SHADOW = 0.45, 0.45, 0.08
# The folds of the red round it: how much lighter the roll (2.3 pixels out) and darker the crease
# (3.8 pixels out) are.
FOLD_ROLL, FOLD_CREASE = 0.1, 0.1

# The eyes: (x, y in the top view, their heat out from the middle as (distance (pixels), heat), how
# much the lens bulges out of the hood and its radius).
EYES = [
    # The big one (columns 7-10, rows 9-12): white-hot, yellow, orange, then dark red into the hood.
    (-3.0, 3.0, [(0.0, 1.3), (0.6, 1.12), (1.0, 0.93), (1.5, 0.7), (2.0, 0.48), (2.5, 0.28), (3.0, 0.04),
                 (3.4, -0.2), (3.8, -0.6)], 0.35, 2.6),
    # The small one (columns 13-15, rows 9-11): orange in the middle, red round it.
    (2.5, 3.5, [(0.0, 0.8), (0.4, 0.74), (0.8, 0.55), (1.2, 0.35), (1.6, 0.15), (2.0, -0.05), (2.4, -0.6)],
     0.22, 1.8),
]

# The molten seam round the lower rim: (angle round the orb's middle in the top view (degrees),
# distance out (a fraction of the radius), heat, half-width (pixels)).
SEAM = [(190, 0.98, 0.0, 0.6), (210, 0.97, 0.5, 0.7), (235, 0.97, 0.52, 0.65), (258, 0.97, 0.5, 0.65),
        (280, 0.95, 0.6, 0.8), (298, 0.91, 0.82, 1.1), (313, 0.86, 1.15, 1.4), (327, 0.89, 0.8, 1.0),
        (343, 0.95, 0.45, 0.75), (358, 0.97, 0.0, 0.6)]
SEAM_GLOW = 0.45  # the red glass lit round the seam: the heat 2.5 half-widths out (of the seam's)
SEAM_SINK = 0.3

# The red glass: its heat (0x72 in the middle of its band) and how much it varies.
BODY, BODY_PATCHES = 0.21, 0.08
BLACK = -0.6

# The bands of heat: (lowest heat, palette index, emission strength in the palette colour).
BANDS = [
    (-9.0, 0x01, 0.0),
    (-0.35, 0x40, 0.0),
    (-0.1, 0x70, 0.0),
    (0.08, 0x71, 0.0),
    (0.17, 0x72, 0.0),
    (0.3, 0x73, 0.0),
    (0.4, 0x74, 0.35),
    (0.48, 0x75, 0.6),
    (0.56, 0x77, 0.8),
    (0.64, 0x78, 1.0),
    (0.72, 0x79, 1.2),
    (0.8, 0x7a, 1.4),
    (0.88, 0x7c, 1.7),
    (0.96, 0x7d, 2.0),
    (1.05, 0x7f, 2.6),
]


def periodic(points, angle):
    """Catmull-Rom through (angle, value) points round a circle (degrees)."""
    angle %= 360.0
    n = len(points)
    for i in range(n):
        a0, v0 = points[i]
        a1, v1 = points[(i + 1) % n]
        span = (a1 - a0) % 360.0
        if (angle - a0) % 360.0 <= span:
            t = ((angle - a0) % 360.0) / span
            vp, vn = points[i - 1][1], points[(i + 2) % n][1]
            return 0.5 * (2 * v0 + (-vp + v1) * t + (2 * vp - 5 * v0 + 4 * v1 - vn) * t * t +
                          (-vp + 3 * v0 - 3 * v1 + vn) * t ** 3)
    return points[0][1]


def direction(p):
    """The direction from the orb's middle to the surface point p, on the unit sphere."""
    rel = p - CENTRE
    return Vector((rel.x / RADII.x, rel.y / RADII.y, rel.z / RADII.z)).normalized()


def hood(p, d):
    """How far inside the hood's outline the point is (pixels; negative outside), seen from above;
    the far side of the orb is outside it."""
    hx, hy = HOOD_MIDDLE[0], HOOD_MIDDLE[1] - FACE_SHIFT
    angle = math.degrees(math.atan2(p.y - hy, p.x - hx))
    inside = periodic(HOOD_OUTLINE, angle) - math.hypot(p.x - hx, p.y - hy)
    return inside if d.z > 0.1 else min(inside, -9.0)


def bump(x, middle, width):
    return math.exp(-((x - middle) / width) ** 2)


def seam_samples(count=180):
    """The seam's middle line, sampled: (direction, heat, half-width)."""
    out = []
    first, last = SEAM[0][0], SEAM[-1][0]
    for i in range(count):
        a = first + (last - first) * i / (count - 1)
        rho = periodic([(s[0], s[1]) for s in SEAM], a)
        heat = periodic([(s[0], s[2]) for s in SEAM], a) * (0.85 + 0.25 * noise.noise(Vector((a * 0.09, 5.0, 1.0))))
        width = periodic([(s[0], s[3]) for s in SEAM], a) * (1 + 0.35 * noise.noise(Vector((a * 0.05, 1.0, 3.0))))
        d = Vector((rho * math.cos(math.radians(a)), rho * math.sin(math.radians(a)),
                    math.sqrt(max(0.0, 1 - rho * rho))))
        out.append((d, max(0.0, heat), width))
    return out


SEAM_SAMPLES = seam_samples()


def seam(d):
    """The seam's heat at direction d, and how deep in its core the point is (0-1)."""
    best, core = 0.0, 0.0
    for c, peak, width in SEAM_SAMPLES:
        dist = d.angle(c) * RADII.x
        if dist > 4 * width:
            continue
        heat = peak * math.exp(-(dist / width) ** 2) + SEAM_GLOW * peak * math.exp(-(dist / (2.5 * width)) ** 2)
        if heat > best:
            best, core = heat, math.exp(-(dist / width) ** 2) * min(1.0, peak * 2)
    return best, core


def radial(profile, r):
    """Linear through (distance, value) points."""
    for (r0, v0), (r1, v1) in zip(profile, profile[1:]):
        if r <= r1:
            return v0 + (v1 - v0) * max(0.0, r - r0) / (r1 - r0)
    return profile[-1][1]


def eye_heat(p):
    heat, lift = -9.0, 0.0
    for x, y, profile, bulge, radius in EYES:
        r = math.hypot(p.x - x, p.y - (y - FACE_SHIFT))
        heat = max(heat, radial(profile, r))
        lift += bulge * max(0.0, 1 - (r / radius) ** 2) ** 2  # a soft lens
    return heat, lift


def heat_and_lift(p):
    d = direction(p)
    # The red glass: patches of lighter and darker red.
    heat = BODY + BODY_PATCHES * noise.noise(d * 2.4 + Vector((1.0, 5.0, 2.0)))
    lift = 0.22 * noise.noise(d * 1.8 + Vector((4.0, 2.0, 7.0)))
    # Round the hood the red lies in folds: shaded under the hood's lip, a lighter roll, a dark crease.
    inside = hood(p, d)
    out = -inside
    if d.z > -0.3:
        fold = 0.6 + 0.4 * noise.noise(d * 3.0 + Vector((7.0, 3.0, 1.0)))
        heat += fold * (FOLD_ROLL * bump(out, 2.3, 0.8) - FOLD_CREASE * bump(out, 3.8, 0.5))
        heat -= HOOD_SHADOW * smoothstep(1.8, 0.3, out)
        lift += fold * (0.28 * bump(out, 2.3, 0.9) - 0.22 * bump(out, 3.8, 0.45))
    # The seam.
    s, core = seam(d)
    heat = max(heat, s)
    lift -= SEAM_SINK * core
    # The hood, raised over the red; its edge shades from black through dark red.
    h = smoothstep(-HOOD_EDGE, HOOD_EDGE, inside)
    heat = heat * (1 - h) + BLACK * h
    lift += HOOD_RAISE * smoothstep(-0.6, 0.5, inside)
    # The eyes in the hood.
    if inside > -1.0:
        e, eye_lift = eye_heat(p)
        heat = max(heat, e)
        lift += eye_lift
    return heat, lift


def orb_mesh(name):
    """An ellipsoid of even triangles (an icosphere), finer on the side the camera sees and finer
    still round the eyes."""
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=4, radius=1.0)

    def point(v):
        d = v.co.normalized()
        return CENTRE + Vector((d.x * RADII.x, d.y * RADII.y, d.z * RADII.z)), d

    def seen(v):
        return point(v)[1].z > -0.15

    def near_eyes(v):
        p, d = point(v)
        return d.z > 0.3 and any(math.hypot(p.x - x, p.y - (y - FACE_SHIFT)) < 3.2 for x, y, *_ in EYES)

    for keep in (seen, near_eyes):
        edges = [e for e in bm.edges if all(keep(v) for v in e.verts)]
        bmesh.ops.subdivide_edges(bm, edges=edges, cuts=1, use_grid_fill=True)
        bmesh.ops.triangulate(bm, faces=bm.faces[:])
        for v in bm.verts:
            v.co.normalize()
    for v in bm.verts:
        v.co = point(v)[0]
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    return obj


def build():
    options = k.args()
    outdir = options.get("outdir", os.path.join(HERE, "..", "..", "..", "..", "assets", "models", "enemies"))
    k.reset()
    # Glossy black and red glass (the black a little metallic, for a sheen); the hotter bands glow in
    # their own colour.
    mats = {}
    for _, index, glow in BANDS:
        mats[index] = k.material(f"orbeyes_{index:x}", palette=index, metallic=0.15 if index < 0x70 else 0.05,
                                 roughness=0.18 if glow < 0.5 else 0.35,
                                 emission=k.level_palette()[index] if glow > 0 else None, emission_strength=glow)
    orb = orb_mesh("orb_eyes")
    values = []
    for v in orb.data.vertices:
        p = v.co.copy()
        heat, lift = heat_and_lift(p)
        values.append(heat)
        v.co = p + direction(p) * lift
    band_split(orb, values, [(lowest, mats[index]) for lowest, index, _ in BANDS])
    k.smooth(orb, 70)
    zs = [v.co.z for v in orb.data.vertices]
    print("== orb_eyes (E 195): %d triangles, %d materials, z %.2f to %.2f" % (
        sum(len(p.vertices) - 2 for p in orb.data.polygons), len(orb.data.materials), min(zs), max(zs)))
    if "check" in options:  # the sheet, or the directory of the exported sheets
        sheet = options["check"]
        k.check_silhouette(os.path.join(sheet, "enemy_E.png") if os.path.isdir(sheet) else sheet, 195)
    # The game shows colours as they are (no filmic tone mapping): so do the previews.
    bpy.context.scene.view_settings.view_transform = "Standard"
    path = os.path.join(outdir, "orb_eyes.glb")
    k.export(path)
    print("%s: %d bytes" % (path, os.path.getsize(path)))
    if "preview" in options:
        k.preview(options["preview"] + "orb_eyes")


if __name__ == "__main__":
    build()
