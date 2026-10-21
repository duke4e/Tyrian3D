"""The armoured eye beetle of MARKERS and TIME WAR (sheet V sprites 197, 199 and 201, 2x2: 19 x 23 pixels in the 24 x 28
cell; episode 2's enemy 815, in the sky, its animation 197 199 201 201 201 199 199 199 197 played once each time it
launches the red ring V 190 (enemy 816, every 20 ticks); episode 4's enemy 676 shows 197 alone on the top layer),
polished (2026-10-21; it replaces wave1_d.py's eye_beetle(), a shell inflated from the sprite's pixels with an ellipsoid
eye). models.cfg: sprite v 197 eye_beetle yaw=0 (unchanged); new: model eye_beetle_199 / eye_beetle_201
enemies/eye_beetle_199.glb / _201.glb, frame v 199 eye_beetle_199, frame v 201 eye_beetle_201.

V 199 and 201 are V 197's pixels but for the eye's and the vents': as it fires, the bright crescent at the eye's left grows
and burns white while the dark pupil at its upper right fades (gone in 201), and the vents heat by two shades a frame. No
other enemy shows V 199 or 201, so they are frame models (the same meshes, only the eye's and the vents' paint changed:
the same bounds, so the game, which centres them in height, keeps them in place). No other sprite of any sheet is these
pixels mirrored, turned or in other ramps; no damaged look (dgr 0).

As the sprite and its 4x upscale draw it (columns and rows of the 24 x 28 cell; symmetric about column 12, x 0.5): a
beetle of steel-blue armour (ramp 3). Its head (rows 2-10): a raised steel rim (columns 6-18) round a big red eye (columns
8-16 of rows 3-10, ramp 7: a dark red ring, a bright crescent at its left, columns 10-11 of rows 5-8, the dark pupil at
its upper right, columns 12-14 of rows 5-7, palette index 0x52), purple plates (ramp 5) curving round its upper sides
like ear guards (columns 3-8 of rows 2-8, lit at column 5 of rows 5-6). A steel chest below it (rows 10-14), lit in its
middle, with a green tube down either side (columns 6-7 and 17-18 of rows 8-15, ramp 2) and a dark seam under it (row
15); the abdomen (rows 16-24): two domed halves either side of a dark groove (column 12), brightest by the groove, two
red vents slanting in towards the bottom (columns 9-10 and 14-15 of rows 20-23), small purple fins at its upper sides
(columns 3-5 and 19-21 of rows 13-19), a notch at its tail (column 12 of row 24).

Built from lofts (tyrkit) as the upscale paints it: the head, the chest and the abdomen lofts across the beetle whose
sections follow the sprite's outline (the abdomen's tops two domes either side of the groove); the eye a painted ball
(polish_balls) in a rim turned round it, its heat painted as the game's slanted camera sees it (polish_dark_orb.py's
VIEW_TILT: the ball's face high on it shows where the sprite draws it), glowing in its own reds (well under 1: the bloom
adds); the vents painted lenses sunk into the halves; the purple plates and fins tapering horns along their curves
(polish_twin_claw.horn), the tubes and the seam thin bars laid on the surfaces (polish_green_beetle.thin_tube), glowing a
little green. The left half's parts are built and mirrored.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera; origin at the sprite's
centre (pixel 12, 14): column c is x = c + 0.5 - 12, row r is y = 13.5 - r; the beetle is built about u = x - 0.5 = 0 and
moved there. A flying object: the game centres it in height.

Replaces wave1_d.py's eye_beetle() (its "# --- The eye beetle (sheet V 197)" section: SPRITE_ORIGIN, which ring_frame()
also reads, stays; the @model("eye_beetle", "V", 197) registration and the eye_beetle() function go, with the docstring's
eye_beetle line and the "import numpy as np", which only eye_beetle() uses) and wave1_d_art.py's BEETLE (only
eye_beetle() reads it): remove them so that they don't overwrite these models.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (each frame's silhouette against
enemy_V.png), --preview <prefix>, --only <name,...>, --stats 1.
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
from polish_green_beetle import thin_tube  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402
from polish_redjet import Curve  # noqa: E402
from polish_swirl_machine import loft_top  # noqa: E402
from polish_twin_claw import horn, paint_sections  # noqa: E402

AXIS_X = 0.5                # the sprite's middle (column 12)
VIEW_TILT = 20.0            # the eye is painted as the game's camera sees it (polish_dark_orb.py)

# --- The body --------------------------------------------------------------------------------------------------------
# Each loft: half-width by y (pixel edges, through the middles of the sprite's steps), the height of its sides, of its
# underside; its top's height in the middle by y and its fall across.
HEAD = Curve([(2.6, 7.3, 2.4, 1.0), (4.5, 7.45, 2.5, 1.0), (5.4, 7.2, 2.5, 1.0), (6.3, 6.65, 2.5, 1.0),
              (8.4, 6.5, 2.5, 1.0), (9.5, 5.6, 2.4, 1.1), (10.5, 4.6, 2.3, 1.2), (11.35, 3.6, 2.2, 1.3),
              (11.85, 2.4, 2.1, 1.4), (12.05, 1.0, 2.0, 1.5)])
HEAD_Y = (2.55, 12.08)
HEAD_TOP = Curve([(2.55, 4.6), (5.0, 5.0), (8.0, 5.1), (10.5, 4.7), (12.08, 3.6)])
HEAD_FALL = 0.03
CHEST = Curve([(-2.3, 6.5, 2.3, 1.0), (-1.0, 6.55, 2.4, 1.0), (1.0, 6.5, 2.5, 1.0), (2.6, 6.2, 2.5, 1.0),
               (3.6, 5.2, 2.5, 1.0), (4.2, 3.6, 2.5, 1.0)])
CHEST_Y = (-2.35, 4.25)
CHEST_TOP = Curve([(-2.35, 4.6), (-1.2, 5.6), (0.5, 6.15), (2.0, 6.2), (3.4, 5.8), (4.25, 5.2)])
CHEST_FALL = 0.05
ABDOMEN = Curve([(-11.05, 0.8, 2.0, 1.5), (-10.9, 2.4, 2.1, 1.4), (-10.4, 4.0, 2.2, 1.3), (-9.5, 5.55, 2.3, 1.2),
                 (-8.5, 6.4, 2.4, 1.1), (-7.5, 6.95, 2.4, 1.0), (-6.5, 7.45, 2.5, 1.0), (-4.5, 7.6, 2.5, 1.0),
                 (-2.6, 7.45, 2.5, 1.0), (-1.6, 7.0, 2.4, 1.0), (-1.2, 6.6, 2.3, 1.0)])
ABDOMEN_Y = (-11.08, -1.15)
ABDOMEN_TOP = Curve([(-11.08, 3.6), (-10.0, 4.7), (-8.0, 5.5), (-5.0, 5.9), (-2.6, 5.6), (-1.15, 4.7)])
ABDOMEN_FALL = 0.075
GROOVE = (0.55, 0.95)        # the groove between the halves: half-width, depth
NOTCH = (0.7, -10.2)         # the tail's notch: half-width, where it starts (y)
# The eye (columns 8-16 of rows 3-10) and the rim round it: (radius out from the eye's middle across and along, as
# fractions of its plan radii, height) from the inner lip out (two pixels wide at the eye's sides, one at its top).
EYE = Ellipsoid((0.0, 7.05, 4.65), (4.45, 4.05, 2.9))
RIM = [(0.97, 0.97, 5.3), (1.03, 1.02, 5.8), (1.1, 1.065, 6.0), (1.19, 1.11, 5.92), (1.29, 1.16, 5.5),
       (1.37, 1.2, 4.85), (1.42, 1.22, 4.0)]
# The left vent (columns 9-10 of rows 20-23): middle, radii (across, along, up), turned about z (degrees).
VENT = ((-2.55, -8.0), (1.0, 2.15, 0.8), 18.4)
# The purple plates (left): the upper one round the head, the fin at the abdomen's side: (u, y, z, half-width in plan,
# half-height) from end to end.
PLATE = [(-8.0, 5.15, 3.0, 0.4, 0.35), (-8.55, 6.4, 3.5, 1.0, 0.9), (-8.2, 7.7, 3.9, 1.4, 1.1),
         (-7.4, 9.1, 4.2, 1.5, 1.2), (-6.25, 10.35, 4.4, 1.5, 1.2), (-5.15, 11.3, 4.4, 1.3, 1.1),
         (-4.25, 11.85, 4.3, 0.8, 0.75), (-3.75, 12.0, 4.2, 0.25, 0.25)]
FIN = [(-7.9, 0.9, 2.8, 0.35, 0.3), (-8.0, 0.0, 3.2, 1.1, 0.9), (-8.15, -1.3, 3.4, 1.35, 1.05),
       (-8.45, -2.7, 3.4, 1.15, 0.95), (-8.5, -4.0, 3.2, 0.95, 0.8), (-8.25, -5.2, 2.9, 0.6, 0.5),
       (-7.9, -5.85, 2.7, 0.2, 0.2)]
# The left green tube (columns 6-7 of rows 8-15) and the seam under the chest (row 15).
TUBE = [(-6.0, 5.7), (-5.6, 4.2), (-5.1, 2.6), (-5.0, 0.6), (-5.0, -1.3)]
SEAM = [(-6.2, -1.55), (-3.0, -1.6), (0.0, -1.62), (3.0, -1.6), (6.2, -1.55)]

# --- The frames ----------------------------------------------------------------------------------------------------
# Per frame: the eye's crescent (in the view of the eye, its plan radii 1: its radius, width, the angle of its hottest
# part (degrees, 0 to the right, counter-clockwise), its angular half-width, its peak) and a glow in its middle (weight,
# a, b, radius) or None, the pupil's (a, b, width, height) or None, the band colours (body, warm, glow, hot) and the
# vents' heat scale. 197: a C-shaped crescent at the eye's left, hottest low on it, the pupil at its upper right; 199:
# the crescent broader and hotter, the pupil smaller; 201: white-hot, the glow spread to the middle, no pupil.
FRAMES = [
    ("eye_beetle", 197, (0.43, 0.13, 205.0, 62.0, 1.0), None, (0.27, 0.08, 0.24, 0.29), (0x72, 0x75, 0x79, 0x7b), 1.0),
    ("eye_beetle_199", 199, (0.42, 0.16, 200.0, 72.0, 1.15), (0.35, -0.1, -0.15, 0.3), (0.3, 0.1, 0.16, 0.2),
     (0x72, 0x77, 0x7a, 0x7e), 1.3),
    ("eye_beetle_201", 201, (0.4, 0.2, 195.0, 85.0, 1.3), (0.75, 0.0, -0.05, 0.42), None, (0x73, 0x78, 0x7c, 0x7f),
     1.6),
]
HEAT_BANDS = (0.25, 0.5, 0.8)


def materials(colours):
    pal = k.level_palette()
    body, warm, glow, hot = colours

    def steel(name, index, metallic=0.55, roughness=0.26):
        return k.material(name, palette=index, metallic=metallic, roughness=roughness)

    def lit(name, index, strength, roughness=0.12, metallic=0.1, glow_index=None):
        return k.material(name, palette=index, metallic=metallic, roughness=roughness,
                          emission=pal[glow_index or index], emission_strength=strength)
    return {
        "steel": steel("ebt_steel", 0x3b, 0.55, 0.25),
        "pale": steel("ebt_pale", 0x3c, 0.5, 0.22),
        "light": steel("ebt_light", 0x3d, 0.5, 0.2),
        "dark": steel("ebt_dark", 0x35, 0.45, 0.38),
        "purple": k.material("ebt_purple", palette=0x59, metallic=0.35, roughness=0.26),
        "purple_light": k.material("ebt_purple_light", palette=0x5c, metallic=0.35, roughness=0.22),
        "purple_dark": k.material("ebt_purple_dark", palette=0x55, metallic=0.3, roughness=0.38),
        "tube": lit("ebt_tube", 0x29, 0.22, 0.25, 0.2, 0x2a),
        "rim": lit("ebt_eye_rim", 0x70, 0.3, glow_index=0x73),
        "body": lit("ebt_eye_%x" % body, body, 0.35, glow_index=body + 2),
        "warm": lit("ebt_eye_%x" % warm, warm, 0.45),
        "glow": lit("ebt_eye_%x" % glow, glow, 0.55),
        "hot": lit("ebt_eye_%x" % hot, hot, 0.62),
        "pupil": k.material("ebt_pupil", palette=0x52, metallic=0.2, roughness=0.15),
    }


# --- Helpers ---------------------------------------------------------------------------------------------------------

def centred(table):
    def f(y):
        hw, zc, zb = table(y)
        return 0.0, hw, zc, zb
    return f


def gauss(x, y, w, h):
    return math.exp(-(x / w) ** 2 - (y / h) ** 2)


def eye_view(p):
    """Where the point p of the eye's surface shows as the game's camera sees it, in the eye's plan radii (a across,
    b up the screen), and whether the camera sees it."""
    t = math.radians(VIEW_TILT)
    rel = p - EYE.centre
    rx, ry, rz = EYE.radii
    h = math.hypot(ry * math.cos(t), rz * math.sin(t))
    a = rel.x / rx
    b = (rel.y * math.cos(t) + rel.z * math.sin(t)) / h
    normal = Vector((rel.x / rx ** 2, rel.y / ry ** 2, rel.z / rz ** 2))
    return a, b, normal.dot(Vector((0.0, -math.sin(t), math.cos(t)))) > 0.0


def eye_paint(heat, pupil):
    def rim(p, n):
        a, b, seen = eye_view(p)
        return math.hypot(a, b) if seen else 2.0

    radius, width, angle, spread, peak = heat[0]
    middle = heat[1]

    def hot(p, n):
        a, b, seen = eye_view(p)
        if not seen:
            return 0.0
        rho = math.hypot(a, b)
        off = (math.degrees(math.atan2(b, a)) - angle + 180.0) % 360.0 - 180.0
        value = peak * math.exp(-((rho - radius) / width) ** 2 - (off / spread) ** 2)
        if middle is not None:
            w, ca, cb, r = middle
            value += w * gauss(a - ca, b - cb, r, r)
        return value
    paint = [(rim, (0.84,), ("body", "rim")), (hot, HEAT_BANDS, (None, "warm", "glow", "hot"))]
    if pupil is not None:
        pa, pb, pw, ph = pupil

        def dark(p, n):
            a, b, seen = eye_view(p)
            return gauss(a - pa, b - pb, pw, ph) if seen else 0.0
        paint.append((dark, (0.5,), (None, "pupil")))
    return paint


def head_top(x, y):
    return HEAD_TOP(y) - HEAD_FALL * x * x


def chest_top(x, y):
    return CHEST_TOP(y) - CHEST_FALL * x * x


def abdomen_top(x, y):
    u = abs(x)
    z = ABDOMEN_TOP(y) - ABDOMEN_FALL * max(0.0, u - 1.4) ** 2
    w, d = GROOVE
    z -= d * math.exp(-(x / w) ** 2)
    nw, ny = NOTCH
    if y < ny:
        z -= 2.5 * math.exp(-(x / nw) ** 2) * min(1.0, (ny - y) / 0.8)
    return z


def on(surface, points, lift=0.0):
    out = []
    for x, y in points:
        hit = surface(x, y)
        out.append(Vector((x, y, (hit[0].z if hit else 4.0) + lift)))
    return out


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


# --- The parts -------------------------------------------------------------------------------------------------------

def body(m):
    head = loft_top("head", centred(HEAD), HEAD_Y, head_top, (2.6, 2.0), m["steel"], 18, 40)
    chest = loft_top("chest", centred(CHEST), CHEST_Y, chest_top, (2.6, 2.0), m["steel"], 14, 40)
    abdomen = loft_top("abdomen", centred(ABDOMEN), ABDOMEN_Y, abdomen_top, (2.6, 2.0), m["pale"], 22, 44)
    for obj in (head, chest):
        mk.paint(obj, lambda c, n: m["dark"] if n.z < 0.15 else None)
    # The groove between the halves dark.
    mk.paint(abdomen, lambda c, n: m["dark"] if abs(c.x) < 0.35 and n.z > 0.15 else None)
    return [head, chest, abdomen]


def ring_lathe(name, profile, centre, mat, segments=40):
    """A closed ring turned about a vertical axis: profile [(radius across, radius along, z), ...] a closed loop (its
    last point joins its first)."""
    cx, cy = centre
    n = len(profile)
    verts, faces = [], []
    for j in range(segments):
        a = 2 * math.pi * j / segments
        for rx, ry, z in profile:
            verts.append((cx + rx * math.cos(a), cy + ry * math.sin(a), z))
    for j in range(segments):
        for i in range(n):
            a0, a1 = j * n + i, j * n + (i + 1) % n
            b0, b1 = ((j + 1) % segments) * n + i, ((j + 1) % segments) * n + (i + 1) % n
            faces.append((a0, a1, b1, b0))
    obj = k.mesh_object(name, verts, faces, mat)
    k.recalc_normals(obj)
    return obj


def eye(m, heat, pupil):
    ball = painted_ball("eye", EYE, eye_paint(heat, pupil), m, subdivisions=4, smooth_angle=80)
    rx, ry, _ = EYE.radii
    cx, cy, _ = EYE.centre
    profile = [(rx * fx, ry * fy, z) for fx, fy, z in RIM]
    profile += [(rx * RIM[-1][0], ry * RIM[-1][1], 2.6), (rx * RIM[0][0], ry * RIM[0][1], 2.6)]
    rim = ring_lathe("eye_rim", profile, (cx, cy), m["steel"])
    k.smooth(rim, 60)
    mk.paint(rim, lambda c, n: m["light"] if n.z > 0.75 else m["dark"] if n.z < 0.2 else None)
    return [ball, rim]


def vent(m, surface, scale):
    (x, y), radii, turn = VENT
    hit = surface(x, y)
    z = (hit[0].z if hit else 5.0) - 0.38
    shape = Ellipsoid((0.0, 0.0, 0.0), radii)

    def heat(p, n):
        if n.z <= 0.15:
            return 0.0
        return scale * gauss(p.x + 0.1, p.y - 0.55, 0.42, 0.85)
    obj = painted_ball("vent_l", shape, [(lambda p, n: n.z, (0.42,), ("rim", "body")),
                                         (heat, (0.45, 0.95), (None, "warm", "glow"))], m, subdivisions=3,
                       smooth_angle=80)
    obj.data.transform(Matrix.Translation((x, y, z)) @ Matrix.Rotation(math.radians(turn), 4, "Z"))
    return obj


def plates(m):
    plate, pc = horn("plate_l", PLATE, m["purple"], 10)
    paint_sections(plate, pc, 10, lambda c, n: m["purple_dark"] if n.z < 0.15 else
                   m["purple_light"] if n.z > 0.55 and n.x < -0.2 else None)
    fin, fc = horn("fin_l", FIN, m["purple"], 10)
    paint_sections(fin, fc, 10, lambda c, n: m["purple_dark"] if n.z < 0.15 else
                   m["purple_light"] if n.z > 0.55 and n.x < -0.2 else None)
    return [plate, fin]


def beetle(frame):
    name, sprite, crescent, middle, pupil, colours, vent_scale = frame
    heat = (crescent, middle)
    m = materials(colours)
    parts = body(m)
    bpy.context.view_layer.update()
    surface = mk.surface(parts)
    parts += eye(m, heat, pupil)
    parts.append(thin_tube("seam", on(surface, SEAM, -0.15), 0.42, m["dark"], 6, squash=0.6, iterations=1))
    left = plates(m) + [vent(m, surface, vent_scale)]
    left.append(thin_tube("tube_l", on(surface, TUBE, -0.05), 0.55, m["tube"], 8, squash=0.8))
    parts += left + mirrored(left)
    mk.transform(parts, Matrix.Translation((AXIS_X, 0.0, 0.0)))
    return parts


def build():
    options = k.args()
    out = mk.outdir(options)
    only = set(options["only"].split(",")) if "only" in options else None
    for frame in FRAMES:
        name, sprite = frame[0], frame[1]
        if only and name not in only:
            continue
        k.reset()
        parts = beetle(frame)
        triangulate(parts)
        bpy.context.view_layer.update()
        if "stats" in options:
            for obj in parts:
                print("  %-16s %5d triangles" % (obj.name, len(obj.data.polygons)))
        if "check" in options:
            sheet = os.path.join(options["check"], "enemy_V.png")
            mk.compare("%s (V %d)" % (name, sprite), mk.coverage(parts, 24, 28), k.sprite_mask(sheet, sprite))
        bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
        mk.report(name, parts, os.path.join(out, name + ".glb"))
        if "preview" in options:
            mk.preview(options["preview"] + name, parts, distance=0.7)


if __name__ == "__main__":
    build()
