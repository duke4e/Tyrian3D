"""FRUIT's grape wing (sheet ', written x27 in models.cfg: sprites 130 and 132, 2x2 each; enemies 1227 and 1228 of
episode 5, one frame each): a bunch of pale grapes round a glossy purple pod, two strings of grapes hanging under it,
on a dark purple wing with a pale rib and spur at each tip. Polished (2026-10-21; it replaces wave3_ae.py's grape
wing). The levels always put its two sprites side by side as one 48 x 28 picture (FRUIT's events 850-4640: 1227 (' 130)
at (x, y) and 1228 (' 132) at (x + 24, y), the same link, 20 pairs; type 15 in the sky, type 10 on the ground2 layer
at 4590 and 4640); each is an enemy of its own (the two move together, one can be shot away first). Only these two
enemies show the sprites (launched ones included), and neither is another sprite's pixels mirrored, turned or in other
ramps; the picture is its own mirror image in coverage (IoU 0.997; its shading is not, lit from one side), its 23
grapes at mirror images of each other's places (one on the seam): so the object is built symmetric.

As the sprites and their 4x upscales draw it (columns and rows of the 48 x 28 picture; purples of ramp 5): the wing a
band across the whole width (rows 5-14, its top edge straight at row 5, its trailing edge at row 14 with a notch a
pixel high at columns 3-5 and 42-44), dark (0x54, 0x52-0x53 under the bunch), its top and trailing edges rolled
(the upscale's rims), a lit fold in its lower outer part (0x58-0x5c: columns 3-10 of rows 8-13, and 38-44 of rows 9-13);
at each tip a pale rib (columns 1 and 46, rows 4-14) running on below the wing as a pale spur (rows 15-19, lighter to
its point); in the middle the pod (columns 21-26 of rows 3-17), a glossy teardrop narrowing to its top, lit in its
middle (0x5a-0x5c), its rim darker (0x55, 0x57), a white glint (0x7f) at columns 23-24 of rows 12-13; round it the
grapes, each the same 4 x 4 ball (0x59 0x5a at its lower left to 0x5c 0x5d, a highlight 0x5e at its upper right):
one over the pod's tip, ten either side round it and under it, and under the bunch on each side two more strung on a
stalk (the darker 0x55 between them), going down and curling in (GRAPE_TOP, GRAPES_LEFT: their middles).

Built as such a creature: the wing a solid over its outline (polish_ring_machine.relief: its top the membrane, a
rolled spar along its top edge and a rolled trailing edge, sagging between them, bulging in the fold, its edges
rounded; painted dark, the rolls and the fold's crease and flap lit, its rim matte), bent down towards its tips (ARCH),
the fold fading out under the ribs; the ribs
tubes down the wing's ends tapering into the spurs; the pod a glossy teardrop (painted_ball of polish_balls.py on a
narrowing ellipsoid: its rim darker as the slanted camera sees it, a small glint at its upper left where the game's
sun puts it); the grapes icospheres on a dome over the wing (higher next to the pod, the strings hanging lower), ten
more behind them filling the bunch out (GRAPES_BACK), each painted with a darker rim (as the slanted camera sees it)
and a lit cap at its upper left (the game's sun: the sprite lights them from the upper right; the game's own
highlight is their glint), glowing faintly in their own colours (0.1-0.18) so that they don't read dark; thin
stalks through the strings' grapes. The whole is built and cut along the sprites' edge (x = 0: polish_savara_boss.cut,
which keeps each face's winding; the cuts closed in each part's own colour, shown only when a piece is shot away),
each piece moved so that its sprite's centre is its origin, its parts joined into one mesh, every mesh triangulated
before the export (polish_k_pod.triangulate: the output is the same with and without --check).

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z towards the camera. The whole's origin
is the middle of the picture (its pixel edge 24, 14, on the seam): column c is x = c + 0.5 - 24, row r is
y = 13.5 - r. The pieces' centres: 130 (-12, 0), 132 (12, 0). The wing lies at about z 0-2 (lower at its tips), the
bunch rises to z 9 (origin models are drawn at their origin: the sky layer's height, or 4 pixels over the terrain on
the ground2 layer). models.cfg (unchanged): model grape_wing_l / grape_wing_r enemies/grape_wing_*.glb origin, sprite
x27 130 grape_wing_l yaw=0, sprite x27 132 grape_wing_r yaw=0.

Replaces wave3_ae.py's grape wing (all that is left of it: GRAPES, grape_spots(), grape_wing_whole(), the
kit.PROTECT += ["gpod"] line and the kit.pieced("grape_wing", ...) registration, its docstring paragraph): with it the
whole file goes; and wave3_ae_art.py's GRAPES (read only by wave3_ae.py).

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouettes of the whole
and of each piece against enemy_x27.png), --preview <prefix> (the whole's top and 3/4 views; --pieces 1 also each
piece's), --only <model,...>, --whole <file.glb> (the uncut whole as well, for looking at).
"""
import math
import os
import random
import sys

import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polish_machine_kit as mk  # noqa: E402
from polish_machine_kit import k  # noqa: E402
from polish_balls import Ellipsoid, painted_ball  # noqa: E402
from polish_deli_boss import join  # noqa: E402
from polish_k_pod import triangulate  # noqa: E402
from polish_ring_machine import ccw, chaikin, relief, round_edge  # noqa: E402
from polish_savara_boss import cut  # noqa: E402
from polish_sphere_nozzle import smoothstep  # noqa: E402

PIECES = [("grape_wing_l", 130, (-24.0, 0.0, -14.0, 14.0)), ("grape_wing_r", 132, (0.0, 24.0, -14.0, 14.0))]

VIEW_TILT = 20.0                     # the game's camera: degrees off straight down, from the bottom of the screen
T = math.radians(VIEW_TILT)
TOWARDS_VIEW = Vector((0.0, -math.sin(T), math.cos(T)))
SUN = Vector((-0.6, 0.6, 1.0)).normalized()   # towards the game's sun (render_gpu.c: from above and the top left)

# --- The wing ------------------------------------------------------------------------------------------------------
# Its outline's left half (pixel edges: x, y), from the top middle round the tip to the bottom middle: the top edge
# (row 5), the tip (column 0), the trailing edge (row 14) with its notch (columns 3-5).
WING_LEFT = [(0.0, 9.0), (-21.0, 9.0), (-23.2, 8.95), (-23.9, 8.4), (-23.95, 6.0), (-23.95, 0.0), (-23.85, -0.75),
             (-23.2, -1.0), (-21.9, -1.0), (-21.2, -0.2), (-20.4, 0.05), (-18.7, 0.05), (-18.0, -0.35),
             (-17.3, -1.0), (-6.0, -1.0), (0.0, -1.0)]
WING_Z, WING_BOTTOM = 1.2, 0.6       # the membrane's top (before the rolls, the sag and the fold) and its underside
SPAR = (8.25, 0.75, 0.75)            # the rolled top edge: its middle (y), half-width, height over the membrane
TRAIL = (-0.2, 0.7, 0.5)             # the rolled trailing edge
SAG = 0.25                           # the membrane sags between them
# The fold: the wing's lower outer corner turned up along a crease (the left wing's: a triangle between the rib and
# the trailing edge, its long side the crease, (x, y) of its corners), rising to FOLD_H towards the corner.
FOLD = ((-21.7, 6.2), (-21.7, -1.2), (-12.8, -1.2))
FOLD_H = 0.55
CREASE = (0.1, 0.75)                 # the crease's lit band: from this far inside the fold to this far
EDGE_ROUND = 0.45                    # the outline's rounding
ARCH = 1.6                           # how much lower the tips are than the middle

# --- The ribs and spurs: x, from the wing's top down to the spur's point (y, radius, z lift over the wing) -----------
RIB_X = -22.55
RIB = [(9.6, 0.5, 0.35), (8.6, 0.62, 0.45), (5.0, 0.66, 0.45), (1.0, 0.64, 0.4), (-1.1, 0.56, 0.25),
       (-3.0, 0.42, 0.0), (-4.8, 0.24, -0.25), (-6.1, 0.05, -0.45)]

# --- The pod: its middle, radii (across, along, height), how much it narrows towards its top ---------------------------
POD_C, POD_R, POD_TAPER = Vector((0.0, 3.4, 4.3)), (3.2, 7.6, 3.2), 0.42
POD_GLINT = (Vector((-0.8, 2.4)), 0.55)  # the glint: its place seen from above and its size

# --- The grapes: their middles (pixel edges of the sprite's 4 x 4 balls), the left half and the one on the seam -----
GRAPES_LEFT = [(-4.0, 11.0), (-8.0, 10.0), (-5.0, 7.0), (-9.0, 6.0), (-6.0, 3.0), (-9.0, 0.0), (-5.0, -1.0),
               (-2.0, -4.0), (-6.0, -5.0), (-7.0, -9.0), (-4.0, -12.0)]
GRAPE_TOP = (0.0, 12.0)
STRING = [(-6.0, -5.0), (-7.0, -9.0), (-4.0, -12.0)]   # the hanging string's grapes (the left one)
GRAPE_R = (2.32, 2.32, 2.1)
# Grapes behind the front ones, filling the bunch out where the sprite shows its dark gaps (left half; a little lower).
GRAPES_BACK = [(-6.6, 8.6), (-7.4, 4.4), (-7.3, 1.2), (-3.6, -2.4), (-2.2, 8.4)]
BACK_DROP = 1.3
GRAPE_Z0, GRAPE_DOME = 3.4, 3.1      # the grapes' middles: on a dome over the wing, highest next to the pod
STRING_Z = (4.2, 3.4, 2.9)           # the string's grapes, lower and lower
STALK_R = 0.32

# The materials: (name, palette index, metallic, roughness, emission strength in its own colour or None)
MATS = [
    ("wing", 0x54, 0.3, 0.24, None), ("wing_dark", 0x52, 0.1, 0.65, None), ("wing_light", 0x58, 0.3, 0.22, None),
    ("roll", 0x56, 0.3, 0.22, None), ("rib", 0x5b, 0.15, 0.35, 0.08), ("spur", 0x5c, 0.1, 0.3, 0.14),
    ("pod_rim", 0x57, 0.2, 0.18, 0.12), ("pod", 0x5a, 0.2, 0.15, 0.16), ("pod_glint", 0x7f, 0.0, 0.1, 0.35),
    ("grape_dark", 0x59, 0.0, 0.36, 0.1), ("grape", 0x5b, 0.0, 0.32, 0.14), ("grape_lit", 0x5c, 0.0, 0.3, 0.18), ("stalk", 0x56, 0.1, 0.5, None),
]


def materials():
    pal = k.level_palette()
    m = {}
    for name, index, metallic, roughness, glow in MATS:
        extra = dict(emission=pal[index], emission_strength=glow) if glow else {}
        m[name] = k.material(f"gwing_{name}", palette=index, metallic=metallic, roughness=roughness, **extra)
    return m


def grapes():
    right = [(-x, y) for x, y in GRAPES_LEFT]
    return [GRAPE_TOP] + GRAPES_LEFT + right


def back_grapes():
    return GRAPES_BACK + [(-x, y) for x, y in GRAPES_BACK]


def arch(x):
    return -ARCH * (x / 24.0) ** 2


# --- The wing ------------------------------------------------------------------------------------------------------

def wing_outline():
    left = WING_LEFT
    right = [(-x, y) for x, y in reversed(left[1:-1])]
    return ccw(chaikin(left + right, 2))


def roll(y, spec):
    mid, half, height = spec
    t = (y - mid) / half
    return height * math.sqrt(max(0.0, 1.0 - t * t))


def fold(x, y):
    """How far inside the fold's triangle (x, y) lies (from its crease, the long side; negative outside), mirrored for
    the right wing."""
    (ax, ay), (bx, by), (cx, cy) = FOLD
    px_, py_ = -abs(x), y
    # the crease from (ax, ay) to (cx, cy): the corner (bx, by) on its inner side
    dx, dy = cx - ax, cy - ay
    length = math.hypot(dx, dy)
    nx_, ny_ = -dy / length, dx / length
    if (bx - ax) * nx_ + (by - ay) * ny_ < 0:
        nx_, ny_ = -nx_, -ny_
    return (px_ - ax) * nx_ + (py_ - ay) * ny_


def fold_lift(x, y):
    """The fold's rise, fading out under the rib (so that the tip's edge stays low and matte there)."""
    return FOLD_H * smoothstep(0.0, 2.2, fold(x, y)) * smoothstep(23.9, 22.4, abs(x))


def membrane(x, y):
    t = (y - 4.0) / 4.6
    return WING_Z - SAG * max(0.0, 1.0 - t * t) + max(roll(y, SPAR), roll(y, TRAIL)) + fold_lift(x, y)


def wing(m):
    def height(x, y, d):
        return WING_BOTTOM + 0.15 + (membrane(x, y) - WING_BOTTOM - 0.15) * round_edge(d, EDGE_ROUND)

    def rolled(x, y, d):
        return max(roll(y, SPAR), roll(y, TRAIL)) / 0.5

    def paint(x, y, d):
        if d < 0.3:
            return "wing_dark"
        f = fold(x, y)
        if f > CREASE[1]:
            return "roll"                          # the flap beyond the crease, a shade lighter
        if f > CREASE[0]:
            return "wing_light"                    # the crease catching the light
        if rolled(x, y, d) > 0.75:
            return "roll"
        return "wing"
    borders = [(lambda x, y, d: d, 0.3), (lambda x, y, d: fold(x, y), CREASE[0]),
               (lambda x, y, d: fold(x, y), CREASE[1]), (rolled, 0.75)]
    obj = relief("wing", [wing_outline()], height, m, paint=paint, side="wing_dark", bottom=WING_BOTTOM, spacing=0.45,
                 borders=borders, smooth_angle=60, band=2.0)
    for v in obj.data.vertices:
        v.co.z += arch(v.co.x)
    obj.data.update()
    return obj


def ribs(m):
    out = []
    for side in (-1, 1):
        pts, radii = [], []
        x = -side * RIB_X
        for y, r, lift in RIB:
            pts.append((x, y, membrane(x, max(y, -0.9)) + arch(x) + lift - 0.2))
            radii.append(r)
        tube = mk.tube(f"rib{side:+d}", pts, 0.5, m["rib"], 12, radii=radii)
        k.smooth(tube, 60)
        mk.paint(tube, lambda c, n: m["spur"] if c.y < -1.2 else None)
        out.append(tube)
    return out


# --- The pod and the grapes ----------------------------------------------------------------------------------------

class Teardrop(Ellipsoid):
    """An ellipsoid narrowing towards its top (+y): x and z scaled down by up to POD_TAPER there."""

    def point(self, d):
        r = self.radii
        s = 1.0 - POD_TAPER * smoothstep(-0.35, 1.0, d.y)
        p = self.centre + Vector((d.x * r.x * s, d.y * r.y, d.z * r.z * s))
        n = Vector((d.x / (r.x * s), d.y / r.y, d.z / (r.z * s))).normalized()
        return p, n


def pod(m):
    shape = Teardrop(POD_C, POD_R)
    (gx, gy), gr = POD_GLINT

    def rim(p, n):
        return n.dot(TOWARDS_VIEW)

    def glint(p, n):
        if n.z <= 0.3:
            return 0.0
        return math.exp(-(((p.x - gx) / gr) ** 2 + ((p.y - gy) / (gr * 1.3)) ** 2))
    paint = [(rim, (0.42,), ("pod_rim", "pod")), (glint, (0.5,), (None, "pod_glint"))]
    return painted_ball("pod", shape, paint, m, subdivisions=4, smooth_angle=80)


def grape_z(x, y):
    for (sx, sy), z in zip(STRING, STRING_Z):
        if abs(abs(x) - abs(sx)) < 0.01 and abs(y - sy) < 0.01:
            return z
    q = (x / 11.5) ** 2 + ((y - 3.0) / 11.0) ** 2
    return GRAPE_Z0 + GRAPE_DOME * max(0.0, 1.0 - q)


def grape(name, centre, radii, m):
    shape = Ellipsoid(centre, radii)
    def rim(p, n):
        return n.dot(TOWARDS_VIEW)

    def lit(p, n):
        return n.dot(SUN)

    paint = [(rim, (0.3,), ("grape_dark", "grape")), (lit, (0.72,), (None, "grape_lit"))]
    return painted_ball(name, shape, paint, m, subdivisions=2, smooth_angle=80)


def bunch(m, rng):
    out = []
    for i, (x, y) in enumerate(grapes()):
        z = grape_z(x, y) + rng.uniform(-0.15, 0.15)
        s = 1.0 + rng.uniform(-0.04, 0.04)
        radii = tuple(r * s * (1.0 + rng.uniform(-0.04, 0.04)) for r in GRAPE_R)
        out.append(grape(f"grape{i}", (x, y, z), radii, m))
    for i, (x, y) in enumerate(back_grapes()):
        z = grape_z(x, y) - BACK_DROP + rng.uniform(-0.1, 0.1)
        out.append(grape(f"grape_back{i}", (x, y, z), tuple(r * 0.95 for r in GRAPE_R), m))
    # The stalks of the hanging strings: from inside the bunch through their grapes.
    for side in (-1, 1):
        left = [(-4.6, -2.6, GRAPE_Z0 + 1.0)] + [(x, y, z) for (x, y), z in zip(STRING, STRING_Z)]
        pts = left if side < 0 else [(-x, y, z) for x, y, z in left]
        stalk = mk.smooth_tube(f"stalk{side:+d}", [p + (STALK_R,) for p in pts], m["stalk"], 8, 3)
        k.smooth(stalk, 60)
        out.append(stalk)
    return out


# --- Build, checks, export -----------------------------------------------------------------------------------------

def build_whole(m):
    rng = random.Random(1227)
    parts = [wing(m)] + ribs(m) + [pod(m)] + bunch(m, rng)
    for obj in parts:
        mk.apply(obj)
    bpy.context.view_layer.update()
    return parts


CAPS = {"wing": "wing_dark", "pod": "pod", "grape": "grape", "stalk": "stalk", "rib": "rib"}


def cap_of(obj, m):
    for prefix, key in CAPS.items():
        if obj.name.startswith(prefix):
            return m[key]
    return m["wing_dark"]


def whole_mask(sheet):
    a, b = k.sprite_mask(sheet, 130), k.sprite_mask(sheet, 132)
    return [ra + rb for ra, rb in zip(a, b)]


def build():
    options = k.args()
    out = mk.outdir(options)
    only = options["only"].split(",") if "only" in options else None
    k.reset()
    m = materials()
    whole = build_whole(m)
    triangulate(whole)  # the cuts are the same every run (with and without --check)
    low, high = mk.bounds(whole)
    print("== whole: %d triangles, %d materials, x %.2f..%.2f y %.2f..%.2f z %.2f..%.2f" % (
        mk.triangles(whole), len(mk.materials_of(whole)), low.x, high.x, low.y, high.y, low.z, high.z))
    sheet = None
    if "check" in options:
        sheets = options["check"]
        sheet = os.path.join(sheets, "enemy_x27.png") if os.path.isdir(sheets) else sheets
        mask = whole_mask(sheet)
        mk.compare("whole (x27 130 + 132)", mk.coverage(whole, 48, 28), mask)
    bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
    if "preview" in options:
        mk.preview(options["preview"] + "grape_wing_whole", whole, size=(48, 28), scale=10, distance=1.6)
    if "whole" in options:
        mk.export(whole, options["whole"])
    for name, sprite, box in PIECES:
        if only and name not in only:
            continue
        parts = [cut(src, box, cap_of(src, m)) for src in whole]
        parts = [p for p in parts if p is not None]
        mk.transform(parts, Matrix.Translation((-(box[0] + box[1]) / 2, -(box[2] + box[3]) / 2, 0)))
        bpy.context.view_layer.update()
        triangulate(parts)
        parts = [join(parts, name)]
        parts[0].data.name = name
        for src in whole:
            src.hide_render = True
        if sheet:
            c0 = 0 if box[0] < 0 else 24
            mk.compare("%s (x27 %d)" % (name, sprite), mk.coverage(parts, 24, 28),
                       [row[c0:c0 + 24] for row in mask])
        mk.report(name, parts, os.path.join(out, name + ".glb"))
        if "preview" in options and options.get("pieces") == "1":
            mk.preview(options["preview"] + name, parts)
        for obj in parts:
            bpy.data.objects.remove(obj)
        for src in whole:
            src.hide_render = False


if __name__ == "__main__":
    build()
