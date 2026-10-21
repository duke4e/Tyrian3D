"""MARKERS' and MISTAKES' blue steel robot head (sheet V sprite 48, 2x2: 24 x 28 pixels; episode 2's enemy 818, in the
sky in MARKERS (events at 1240, 2750, 3050-3250) and on the ground in MISTAKES (events at 10-80); one frame, not animated;
it shoots), polished (2026-10-21; it replaces wave3_t_ships.py's robot_head(), a helmet and a jaw inflated from the
sprite's pixels with tubes and spheres on them). models.cfg: sprite v 48 robot_head yaw=0 (unchanged).

No damaged look (dgr 0). No other enemy shows V 48, and no other sprite of any sheet is its pixels mirrored, turned or in
other ramps.

As the sprite and its 4x upscale draw it (columns and rows of the 24 x 28 cell; symmetric about the line between columns
11 and 12, x 0): a robot's face of dark blue steel (ramp 3) looking up out of the screen, its brow at the top. The helmet
(rows 0-9): a raised crest down its middle (columns 9-14 of rows 0-8, its sides lit, a dark slot in its top at columns
11-12 of rows 3-6) between two rounded pads (columns 2-7 of rows 1-6, lit at their upper left), a ledge under each with a
small knob (column 6 of row 7); a dark brow (row 9). Under it the visor (rows 10-12): a grey bar (ramp 0) across columns
6-17, its rounded ends lighter and reaching down a row (row 13), the red eye in its middle (columns 11-12, ramp 7,
brightest at its left). Either side a cheek plate (columns 2-5 of rows 10-16), a lit ridge down it (column 3 of rows 8-13).
The jaw below (rows 13-27, narrowing to the chin): two lit ribs down its upper part (columns 10 and 13 of rows 13-17),
the dark mouth slot across it (rows 18-19), four lit ribs down the chin (columns 7, 9, 14 and 16 of rows 20-25) between
dark grooves; grey hinges at its sides (ramp 0, columns 2-5 of rows 17-22), lit at their upper left.

Built as a CAD modeller would, the steel softly rounded as the upscale paints it: the helmet a loft across the face whose
sections follow the sprite's outline; the crest a prism of its plan (polish_machine_kit), its edges well rounded by a
bevel, the slot a dark plate laid into its top (polish_redjet.facet); the pads superellipse domes; the brow and the
visor's socket a dark plate laid into the face, the visor a bar turned about its axis with round end caps, the eye a lens
glowing in its own reds (well under 1: the bloom adds); the cheek plates rounded prisms, the ridges and ribs thin bars laid
on the surfaces (polish_green_beetle.thin_tube), the jaw a loft whose sections narrow to the chin, the mouth slot a dark
plate laid into it, the hinges grey capsules. The left half's parts are built and mirrored.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera; origin at the sprite's
centre (pixel 12, 14): column c is x = c + 0.5 - 12, row r is y = 13.5 - r. Its back on z = 0: the game centres it in
height in the sky and lifts it onto the ground in MISTAKES.

Replaces wave3_t_ships.py's robot_head() (its "# --- V 48: the blue robot head" section with the @model("robot_head",
[48]) registration, and the docstring's robot_head lines) and wave3_t_art.py's ROBOT (only robot_head() reads it; the
ROBOT wave2_e_parts.py reads is wave2_e_art's): remove them so that they don't overwrite this model.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouette against
enemy_V.png sprite 48), --preview <prefix>, --stats 1.
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
from polish_green_beetle import gem_paint, thin_tube  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402
from polish_redjet import Curve, chaikin, facet, resample  # noqa: E402
from polish_swirl_machine import loft_top  # noqa: E402

NAME = "robot_head"

# The helmet (rows 1-9): its half-width by y (pixel edges), the height of its sides, of its underside; its top's height
# in the middle by y and its fall across.
HELMET = Curve([(1.0, 9.9, 2.3, 0.0), (2.4, 10.5, 2.45, 0.0), (3.6, 11.05, 2.6, 0.0), (6.0, 11.1, 2.8, 0.0), (9.5, 11.05, 2.8, 0.0), (10.5, 10.45, 2.7, 0.0),
                (11.5, 9.5, 2.6, 0.0), (12.3, 8.4, 2.5, 0.0), (12.8, 7.2, 2.4, 0.0), (13.05, 5.4, 2.3, 0.0)])
HELMET_Y = (0.95, 13.1)
HELMET_TOP = Curve([(0.95, 4.1), (3.55, 4.6), (5.0, 5.3), (8.0, 5.6), (11.0, 5.5), (13.1, 4.8)])
HELMET_FALL = 0.022
# The crest (columns 9-14 of rows 0-8): its plan, its foot and top; the slot in it (columns 11-12 of rows 3-6).
CREST = [(-3.0, 5.0), (3.0, 5.0), (3.0, 13.35), (2.35, 14.0), (-2.35, 14.0), (-3.0, 13.35)]
CREST_Z = (3.5, 7.9)
SLOT = (-0.95, 0.95, 7.05, 11.0)
# The left pad (columns 2-7 of rows 1-6): its middle, radii (across, along, up) and the height it stands on; the knob on
# the ledge under it (column 6 of row 7).
PAD = ((-6.0, 9.85), (3.25, 3.1, 1.75), 4.2)
KNOB = ((-5.5, 6.45), 0.62)
# The visor's socket (the brow, row 9, and round the visor): its plan; the visor (rows 10-12, columns 6-17): its axis
# (y, z), radius, its ends' caps (x, radius); the eye (columns 11-12 of rows 10-12).
SOCKET = [(-7.2, 4.75), (7.2, 4.75), (7.3, 0.25), (5.2, -0.1), (-5.2, -0.1), (-7.3, 0.25)]
VISOR = (2.45, 5.0, 1.45)
VISOR_X = 4.75
CAP = (5.5, 1.85)
EYE = Ellipsoid((0.0, 2.5, 0.0), (1.15, 1.55, 0.85))
# The left cheek plate (columns 2-5 of rows 10-16, flaring at row 14): its plan, foot and top; its ridge (column 3 of
# rows 8-13).
CHEEK = [(-10.05, 4.1), (-6.0, 4.1), (-6.0, -3.05), (-9.0, -3.05), (-10.15, -1.95), (-10.95, -0.95), (-10.9, 0.0),
         (-10.1, 0.5)]
CHEEK_Z = (1.6, 4.6)
CHEEK_RIDGE = [(-8.5, 5.9), (-8.5, 3.2), (-8.5, 0.3)]
# The jaw (rows 13-27): its half-width by y, the height of its sides, of its underside; its top's height in the middle by
# y and its fall across; the mouth slot (rows 18-19); the ribs (x, y from, y to).
JAW = Curve([(-14.05, 0.6, 2.2, 0.0), (-13.8, 2.2, 2.3, 0.0), (-13.3, 4.3, 2.4, 0.0), (-12.4, 5.2, 2.5, 0.0),
             (-10.5, 6.1, 2.6, 0.0), (-9.5, 6.75, 2.6, 0.0), (-8.5, 6.2, 2.6, 0.0), (-6.0, 6.0, 2.6, 0.0),
             (-3.0, 5.6, 2.6, 0.0), (-0.5, 5.15, 2.6, 0.0), (0.8, 4.9, 2.6, 0.0), (1.6, 4.4, 2.6, 0.0)])
JAW_Y = (-14.1, 1.65)
JAW_TOP = Curve([(-14.1, 3.2), (-12.5, 4.0), (-10.0, 4.6), (-7.0, 5.0), (-4.0, 5.3), (-1.0, 5.4), (1.65, 5.0)])
JAW_FALL = 0.05
MOUTH = [(-4.1, -3.95), (4.1, -3.95), (4.1, -6.05), (-4.1, -6.05)]
RIBS = [(-1.5, 0.4, -3.6), (-4.5, -6.6, -11.9), (-2.5, -6.6, -12.4)]
# The left hinge (columns 2-5 of rows 17-22): its ends (x, y), radius, height.
HINGE = ((-9.55, -4.05), (-7.25, -8.35), 1.6, 2.7)


def materials():
    pal = k.level_palette()

    def steel(name, index, metallic=0.55, roughness=0.26):
        return k.material(name, palette=index, metallic=metallic, roughness=roughness)

    def lit(name, index, strength, roughness=0.15, metallic=0.1, glow=None):
        return k.material(name, palette=index, metallic=metallic, roughness=roughness, emission=pal[glow or index],
                          emission_strength=strength)
    return {
        "steel": steel("rob_steel", 0x39),
        "plate": steel("rob_plate", 0x3a, 0.55, 0.24),
        "light": steel("rob_light", 0x3d, 0.55, 0.2),
        "dark": steel("rob_dark", 0x34, 0.45, 0.4),
        "deep": steel("rob_deep", 0x32, 0.3, 0.55),
        "grey": steel("rob_grey", 0x0a, 0.35, 0.3),
        "grey_light": steel("rob_grey_light", 0x0c, 0.35, 0.24),
        "grey_dark": steel("rob_grey_dark", 0x06, 0.3, 0.4),
        "eye_rim": lit("rob_eye_rim", 0x73, 0.3, glow=0x75),
        "eye": lit("rob_eye", 0x75, 0.45, glow=0x77),
        "eye_core": lit("rob_eye_core", 0x78, 0.6),
    }


# --- Helpers ----------------------------------------------------------------------------------------------------------

def centred(table):
    def f(y):
        hw, zc, zb = table(y)
        return 0.0, hw, zc, zb
    return f


def helmet_top(x, y):
    return HELMET_TOP(y) - HELMET_FALL * x * x


def jaw_top(x, y):
    return JAW_TOP(y) - JAW_FALL * x * x


def ccw(points):
    area = sum(points[i][0] * points[(i + 1) % len(points)][1] - points[(i + 1) % len(points)][0] * points[i][1]
               for i in range(len(points)))
    return points if area > 0 else points[::-1]


def laid(name, outline, surface, mat, sink=0.35, height=0.42, rim=0.14):
    """A thin plate laid into the surface along outline (polish_redjet.facet), standing just proud of it."""
    def base(x, y):
        hit = surface(x, y)
        return (hit[0].z if hit else 4.0) - sink
    return facet(name, ccw(resample(chaikin(outline, 1), 0.55)), base, height, mat, rim=rim, steps=2, dome=0.0,
                 dome_rings=1, sink=0.5)


def on(surface, points, lift=0.0):
    out = []
    for x, y in points:
        hit = surface(x, y)
        out.append(Vector((x, y, (hit[0].z if hit else 4.0) + lift)))
    return out


def rounded_prism(name, outline, z0, z1, mat, bevel):
    obj = mk.prism(name, ccw(outline), z0, z1, mat)
    mk.bevel(obj, bevel, segments=3, angle=30.0)
    return k.smooth(obj, 40)


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


# --- The parts --------------------------------------------------------------------------------------------------------------

def helmet(m):
    obj = loft_top("helmet", centred(HELMET), HELMET_Y, helmet_top, (2.8, 2.0), m["steel"], 22, 40)
    mk.paint(obj, lambda c, n: m["dark"] if n.z < 0.15 else None)
    crest = rounded_prism("crest", CREST, *CREST_Z, m["plate"], 0.75)
    mk.paint(crest, lambda c, n: m["light"] if 0.25 < n.z < 0.9 and abs(n.x) > 0.3 else
             m["dark"] if n.z < 0.2 else None)
    return obj, crest


def slot(m, crest_surface):
    x0, x1, y0, y1 = SLOT
    outline = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    return laid("slot", outline, crest_surface, m["deep"], sink=0.3, height=0.36, rim=0.12)


def pad(m):
    (x, y), (rx, ry, rz), z0 = PAD
    obj = mk.dome("pad_l", (x, y), (rx, ry, rz), z0, m["plate"], segments=32, steps=7, power=5.0)
    return [obj]


def knob(m, surface):
    (kx, ky), kr = KNOB
    hit = surface(kx, ky)
    z = (hit[0].z if hit else 5.0) + 0.05
    return mk.ball("knob_l", (kx, ky, z), (kr, kr, kr * 0.7), m["light"], 12, 6)


def visor(m, face_surface):
    sock = laid("socket", SOCKET, face_surface, m["deep"], sink=0.3, height=0.4, rim=0.2)
    yc, zc, r = VISOR
    segments = 24
    xs = [-VISOR_X + 2 * VISOR_X * i / 12 for i in range(13)]
    rings = [[Vector((x, yc + r * math.cos(2 * math.pi * j / segments), zc + r * 0.8 * math.sin(2 * math.pi * j /
                                                                                              segments)))
              for j in range(segments)] for x in xs]
    bar = k.loft("visor", rings, m["grey"], cap_start=False, cap_end=False)
    k.smooth(bar, 50)
    mk.paint(bar, lambda c, n: m["grey_light"] if n.z > 0.75 and n.y > 0.0 else
             m["grey_dark"] if n.z < 0.2 else None)
    cx, cr = CAP
    caps = []
    for side in (-1, 1):
        cap = mk.ball(f"visor_cap{'lr'[side > 0]}", (side * cx, yc - 0.25, zc - 0.1), (1.05, cr, cr * 0.85), m["grey"],
                      18, 9)
        mk.paint(cap, lambda c, n: m["grey_dark"] if n.z < 0.1 else None)
        caps.append(cap)
    ez = zc + r * 0.8 - 0.35
    eye = painted_ball("eye", Ellipsoid((EYE.centre.x, EYE.centre.y, ez), EYE.radii),
                       gem_paint((-0.35, 2.75), (0.55, 0.75), 0.7, (-0.45, 3.2), (0.3, 0.35), rim_z=0.3),
                       {"rim": m["eye_rim"], "body": m["eye"], "light": m["eye_core"], "core": m["eye_core"]},
                       subdivisions=3, smooth_angle=80)
    return [sock, bar, eye] + caps


def cheek(m):
    plate = rounded_prism("cheek_l", CHEEK, *CHEEK_Z, m["plate"], 0.55)
    mk.paint(plate, lambda c, n: m["dark"] if n.z < 0.2 else None)
    return plate


def jaw(m):
    obj = loft_top("jaw", centred(JAW), JAW_Y, jaw_top, (2.6, 2.0), m["steel"], 25, 40)
    mk.paint(obj, lambda c, n: m["dark"] if n.z < 0.15 else None)
    return obj


def hinge(m):
    (x0, y0), (x1, y1), r, z = HINGE
    a, b = Vector((x0, y0, z)), Vector((x1, y1, z))
    axis = (b - a).normalized()
    rings = []
    segments = 18
    side = axis.cross(Vector((0, 0, 1))).normalized()
    up = side.cross(axis).normalized()
    profile = [(-0.85, 0.35), (-0.65, 0.75), (-0.35, 0.95), (0.0, 1.0), (0.35, 0.95), (0.65, 0.75), (0.85, 0.35)]
    length = (b - a).length
    for t, f in profile:
        c = a + axis * (length * (0.5 + 0.5 * t))
        rings.append([c + (side * math.cos(2 * math.pi * j / segments) + up * 0.7 * math.sin(2 * math.pi * j / segments))
                      * r * f for j in range(segments)])
    obj = k.loft("hinge_l", rings, m["grey"], start_point=a - axis * 0.15, end_point=b + axis * 0.15)
    k.smooth(obj, 60)
    mk.paint(obj, lambda c, n: m["grey_dark"] if n.z < 0.0 else None)
    return obj


def head():
    m = materials()
    hel, crest = helmet(m)
    jw = jaw(m)
    left = [cheek(m), hinge(m)] + pad(m)
    bpy.context.view_layer.update()
    face = mk.surface([hel, jw])
    parts = [hel, crest, jw, slot(m, mk.surface([crest]))] + visor(m, face)
    parts.append(laid("mouth", MOUTH, mk.surface([jw]), m["deep"], sink=0.3, height=0.38, rim=0.16))
    bpy.context.view_layer.update()
    # The ribs and ridges, laid on the surfaces.
    jaw_surface = mk.surface([jw])
    for i, (x, ya, yb) in enumerate(RIBS):
        pts = on(jaw_surface, [(x, ya + (yb - ya) * t / 4) for t in range(5)], -0.12)
        left.append(thin_tube(f"rib{i}_l", pts, 0.36, m["light"], 6, squash=0.7))
    surface = mk.surface([hel, left[0]])
    left.append(thin_tube("cheek_ridge_l", on(surface, CHEEK_RIDGE, -0.1), 0.38, m["light"], 6, squash=0.7))
    left.append(knob(m, mk.surface([hel])))
    return parts + left + mirrored(left)


def build():
    options = k.args()
    out = mk.outdir(options)
    k.reset()
    parts = head()
    triangulate(parts)
    bpy.context.view_layer.update()
    if "stats" in options:
        for obj in parts:
            print("  %-16s %5d triangles" % (obj.name, len(obj.data.polygons)))
    if "check" in options:
        sheet = os.path.join(options["check"], "enemy_V.png")
        mk.compare("robot_head (V 48)", mk.coverage(parts, 24, 28), k.sprite_mask(sheet, 48))
    bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
    mk.report(NAME, parts, os.path.join(out, NAME + ".glb"))
    if "preview" in options:
        mk.preview(options["preview"] + NAME, parts, distance=0.7)


if __name__ == "__main__":
    build()
