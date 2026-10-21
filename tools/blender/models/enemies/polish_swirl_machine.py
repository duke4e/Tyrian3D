"""MARKERS' lilac machine with the blue swirl orb (sheet V sprite 161, 2x2: 24 x 25 pixels in the 24 x 28 cell; episode
2's enemy 817, on the ground; one frame, not animated), polished (2026-10-21; it replaces wave3_t_ships.py's
swirl_machine(), a shell and a body inflated from the sprite's pixels with an ellipsoid orb and tubes). models.cfg: sprite
v 161 swirl_machine yaw=0 (unchanged).

MARKERS' events send it up from the bottom of the screen (ground-bottom events at 160-880, 1320-1370 and 2220-2380, links
10-15): enemy 817 moves up the screen (y move -2 against the ground's scroll), the orb ahead, the glowing red tip behind
it like a thruster; as the sprite draws it (yaw=0). No damaged look (dgr 0); shot, it leaves the game's slumped wreck. No
other enemy shows V 161, and no other sprite of any sheet is its pixels mirrored, turned or in other ramps.

As the sprite and its 4x upscale draw it (columns and rows of the 24 x 28 cell; symmetric about the line between
columns 11 and 12, x 0): a broad lilac shell (ramp 5) like a hood (rows 3-16), its wings sweeping out and down to the
cell's edges (columns 0-3 and 20-23 of rows 10-16), a red streak slanting down each shoulder (columns 2-6 of rows 5-11;
ramp 7); set into its middle a glossy dark blue orb (columns 8-15 of rows 4-15, ramp 9), lit along its left edge and in
a patch at its upper left, a dark swirl like a 2 drawn in it (its darkest pixels are index 0: the ground shows through
them in the game; here a dark line on the orb). Below the orb a grey chrome body (ramp 6, rows 14-25) of two rounded
lobes (white glints at columns 6-7 and 16-17 of rows 17-18) either side of a darker groove; at its bottom a steel-blue
cowl (ramp 3, columns 6-15 of rows 20-25) wrapped round a glowing red tip (columns 10-13 of rows 24-27). Lilac claws
curl down past the body's sides (columns 1-4 and 19-22 of rows 19-27), a dark seam (0x52) between them and the body.

Built from lofts (tyrkit) as the upscale paints it: the shell two wings, each a loft along y whose sections span the
sprite's outline from the wing's outer edge in to the orb, their tops a crest CREST of the way in, falling away to both
edges; the orb a painted ball (polish_balls) in a dark rim, glowing a little in its own blues so that it doesn't read
black from the slanted camera, the swirl a thin dark bar laid on it; the red streaks thin glowing bars set into the
wings; the body a loft whose tops swell into the two lobes about the groove, a dark seam laid down the groove; the cowl
a loft along an arch round the tip, the tip a glowing red lens; the claws tapering horns along their curves
(polish_twin_claw.horn). The left wing, streak and claw are built and mirrored.

Coordinates as in tyrkit: 1 unit = 1 game pixel, +X right, +Y up the screen, +Z up from the ground (z = 0); origin at the
sprite's centre (pixel 12, 14): column c is x = c + 0.5 - 12, row r is y = 13.5 - r. It stands on z = 0 (the game
centres ground models in height and lifts them onto the ground).

Replaces wave3_t_ships.py's swirl_machine() and ellipsoid_z() (its "# --- V 161: the lilac machine with the blue swirl"
section with the @model("swirl_machine", [161]) registration, and the docstring's swirl_machine lines) and
wave3_t_art.py's LILAC (only swirl_machine() reads it): remove them so that they don't overwrite this model.

Options after "--": --outdir <dir> (default assets/models/enemies), --check <sheets dir> (the silhouette against
enemy_V.png sprite 161, and against it with the swirl's see-through pixels counted as the orb's), --preview <prefix>,
--stats 1.
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
from polish_redjet import Curve  # noqa: E402
from polish_twin_claw import horn, paint_sections  # noqa: E402

NAME = "swirl_machine"

# --- The shell ---------------------------------------------------------------------------------------------------------
# The left wing (the right is its mirror image): its plan by y, (y, outer edge, inner edge: pixel edges, through the
# middles of the sprite's steps; the inner edge along the orb), the height of its crest, of its sides, of its underside.
WING = Curve([(-2.95, -9.4, -8.55, 3.1, 1.9, 1.2), (-2.5, -10.25, -8.3, 3.5, 2.0, 1.1), (-1.5, -11.25, -8.0, 4.1, 2.1, 1.0),
              (-0.5, -11.95, -6.2, 4.8, 2.2, 1.0), (0.5, -12.0, -4.3, 5.4, 2.3, 1.0), (2.0, -11.95, -4.1, 5.9, 2.4, 1.0),
              (3.5, -11.75, -4.0, 6.2, 2.4, 1.0), (4.5, -11.25, -3.7, 6.4, 2.4, 1.0), (5.5, -10.7, -2.9, 6.5, 2.4, 1.0),
              (6.5, -9.95, -1.9, 6.5, 2.4, 1.05), (7.5, -9.0, -1.15, 6.4, 2.35, 1.1), (8.5, -8.0, -0.85, 6.2, 2.3, 1.15),
              (9.5, -7.0, -0.85, 5.9, 2.25, 1.25), (10.3, -5.6, -1.0, 5.5, 2.2, 1.35), (10.8, -4.4, -1.55, 5.0, 2.1, 1.5),
              (11.0, -3.4, -2.3, 4.6, 2.0, 1.6)])
WING_Y = (-3.0, 11.05)
SHELL_POWER = (2.3, 2.0)
CREST = 0.62                # where across the wing its crest runs (0 its outer edge, 1 its inner)
# The orb (columns 8-15 of rows 4-15) and its rim; the swirl on it (a 2: from its upper left over the top, down the
# right, across to the lower left and along the bottom).
ORB = Ellipsoid((0.0, 4.25, 3.95), (4.05, 6.0, 3.5))
ORB_RIM = (0.48,)
SWIRL = [(-1.1, 6.6), (-0.1, 7.45), (1.2, 7.3), (2.25, 6.2), (2.55, 4.6), (2.3, 3.1), (1.4, 2.0), (0.1, 1.1),
         (-1.3, 0.25), (-1.65, -0.35), (-0.6, -0.6), (0.9, -0.55), (1.9, -0.25)]
# The red streaks (columns 2-6 of rows 5-11): the left one's points.
STREAK = [(-5.5, 8.6), (-6.6, 7.5), (-7.6, 6.45), (-8.6, 5.35), (-9.35, 4.3), (-9.6, 3.2), (-9.6, 2.3)]

# --- The body ----------------------------------------------------------------------------------------------------------
BODY = Curve([(-12.75, 2.2, 1.9, 1.0), (-12.3, 5.4, 2.0, 0.9), (-11.4, 7.4, 2.1, 0.85), (-10.4, 8.1, 2.2, 0.8),
              (-9.0, 8.6, 2.3, 0.8), (-7.0, 8.8, 2.4, 0.8), (-5.4, 8.5, 2.4, 0.8), (-4.2, 7.7, 2.4, 0.8),
              (-3.2, 6.8, 2.4, 0.8), (-2.2, 6.1, 2.3, 0.8), (-1.2, 5.4, 2.2, 0.85), (-0.4, 4.6, 2.1, 0.9),
              (0.2, 3.4, 2.0, 1.0)])
BODY_Y = (-12.75, 0.3)
BODY_POWER = (2.4, 2.0)
# Its top: the lobes' middles (|x|), heights and radii across; the groove's floor; all by y.
LOBES = Curve([(-12.7, 4.3, 2.6, 3.0), (-10.0, 4.9, 3.6, 3.5), (-7.0, 5.0, 4.6, 3.6), (-4.0, 4.6, 5.1, 3.4),
               (-1.5, 3.8, 4.8, 3.0), (0.3, 3.0, 4.0, 2.6)])
GROOVE_Z = 2.9
# The dark seam down the groove (from under the orb to the cowl).
SEAM = [(0.0, -0.6), (0.0, -2.6), (0.0, -4.6), (0.0, -6.4)]
# The cowl round the tip (columns 6-15 of rows 20-25): its middle line (an arch, from its left foot over the top to the
# right foot), its half-width and height; the tip (columns 10-13 of rows 24-27).
COWL = [(-4.3, -12.3), (-4.6, -10.6), (-4.1, -8.9), (-2.8, -7.6), (-1.2, -6.9), (0.0, -6.8), (1.2, -6.9), (2.8, -7.6),
        (4.1, -8.9), (4.6, -10.6), (4.3, -12.3)]
COWL_HW, COWL_H = 1.45, 1.0
TIP = Ellipsoid((0.0, -11.5, 0.0), (1.75, 2.05, 1.15))
# The left claw: (x, y, z, half-width in plan, half-height) from its top to its tip curling in at the bottom.
CLAW = [(-9.0, -4.9, 2.5, 0.4, 0.35), (-9.7, -5.9, 2.6, 1.1, 0.85), (-10.1, -7.3, 2.65, 1.45, 1.05),
        (-10.2, -8.9, 2.6, 1.5, 1.1), (-10.0, -10.4, 2.45, 1.35, 1.0), (-9.45, -11.7, 2.25, 1.1, 0.85),
        (-8.55, -12.7, 2.0, 0.8, 0.65), (-7.55, -13.4, 1.75, 0.42, 0.36), (-7.0, -13.6, 1.6, 0.12, 0.12)]


def materials():
    pal = k.level_palette()

    def mat(name, index, metallic=0.4, roughness=0.3):
        return k.material(name, palette=index, metallic=metallic, roughness=roughness)

    def lit(name, index, strength, roughness=0.12, metallic=0.1, glow=None):
        return k.material(name, palette=index, metallic=metallic, roughness=roughness, emission=pal[glow or index],
                          emission_strength=strength)
    return {
        "shell": mat("swl_shell", 0x5b, 0.35, 0.25),
        "shell_dark": mat("swl_shell_dark", 0x55, 0.3, 0.38),
        "seam": mat("swl_seam", 0x52, 0.2, 0.55),
        "orb_rim": lit("swl_orb_rim", 0x94, 0.25, glow=0x96),
        "orb": lit("swl_orb", 0x92, 0.25, glow=0x94),
        "orb_light": lit("swl_orb_light", 0x99, 0.38),
        "orb_core": lit("swl_orb_core", 0x9c, 0.5),
        "swirl": mat("swl_swirl", 0x91, 0.2, 0.3),
        "streak": lit("swl_streak", 0x73, 0.3, 0.3, 0.2, glow=0x75),
        "body": mat("swl_body", 0x6b, 0.6, 0.22),
        "body_dark": mat("swl_body_dark", 0x67, 0.55, 0.32),
        "cowl": mat("swl_cowl", 0x3a, 0.6, 0.2),
        "tip": lit("swl_tip", 0x75, 0.45, 0.2, 0.1, glow=0x77),
        "tip_hot": lit("swl_tip_hot", 0x78, 0.55, 0.15, 0.1),
    }


# --- Helpers ------------------------------------------------------------------------------------------------------------

def loft_top(name, table, ys, top_fn, power, mat, count, segments):
    """A loft along y whose sections are superellipses of table(y) = (middle x, half-width, side height, underside),
    their tops following top_fn(x, y) (rounded down to the sides)."""
    y0, y1 = ys
    rings = []
    for i in range(1, count):
        t = i / count
        y = y0 + (y1 - y0) * (0.5 - 0.5 * math.cos(math.pi * t))
        xc, hw, zc, zb = table(y)
        pts = []
        for j in range(segments):
            a = 2 * math.pi * j / segments
            c, s = math.cos(a), math.sin(a)
            p = power[0] if s >= 0 else power[1]
            u = math.copysign(abs(c) ** (2 / p), c)
            v = math.copysign(abs(s) ** (2 / p), s)
            x = xc + hw * u
            z = zc + (max(top_fn(x, y), zc + 0.15) - zc) * v if s >= 0 else zc + (zc - zb) * v
            pts.append(Vector((x, y, z)))
        rings.append(pts)
    xs, _, zs, _ = table(y0)
    xe, _, ze, _ = table(y1)
    obj = k.loft(name, rings, mat, start_point=(xs, y0, zs), end_point=(xe, y1, ze + 0.3))
    return k.smooth(obj, 50)


def wing_table(y):
    _, xo, xi, _, zc, zb = [y] + WING(y)
    return (xo + xi) / 2, (xi - xo) / 2, zc, zb


def body_table(y):
    hw, zc, zb = BODY(y)
    return 0.0, hw, zc, zb


def wing_top(x, y):
    """The left wing's top: a crest CREST of the way in from its outer edge, falling away to both edges."""
    xo, xi, crest, zc, zb = WING(y)
    w = xi - xo
    t = (x - xo) / w
    d = (t - CREST) / (CREST if t < CREST else 1 - CREST)
    return crest - (crest - zc) * 0.55 * d * d


def body_top(x, y):
    u = abs(x)
    c, h, r = LOBES(y)
    lobe = h * math.sqrt(max(0.0, 1 - ((u - c) / r) ** 2))
    return max(GROOVE_Z - 0.04 * u * u, lobe + 0.6)


def on(surface, points, lift=0.0):
    out = []
    for x, y in points:
        hit = surface(x, y)
        out.append(Vector((x, y, (hit[0].z if hit else 3.0) + lift)))
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


# --- The parts ------------------------------------------------------------------------------------------------------------

def shell(m):
    obj = loft_top("wing_l", wing_table, WING_Y, wing_top, SHELL_POWER, m["shell"], 24, 34)
    mk.paint(obj, lambda c, n: m["shell_dark"] if n.z < 0.12 else None)
    return obj


def orb(m):
    mats = {"rim": m["orb_rim"], "body": m["orb"], "light": m["orb_light"], "core": m["orb_core"]}
    ball = painted_ball("orb", ORB, gem_paint((-1.8, 6.4), (1.3, 1.7), 0.75, (-2.0, 7.3), (0.6, 0.7), rim_z=0.42),
                        mats, subdivisions=4, smooth_angle=80)
    # The light along its left edge (the sprite's 0x94 column 8).
    mk.paint(ball, lambda c, n: m["orb_rim"] if n.x < -0.55 and 0.15 < n.z < 0.6 else None)
    rim_z = ORB.centre.z + 0.45
    rim = torus("orb_rim", (ORB.centre.x, ORB.centre.y, rim_z), 1.0, ORB_RIM[0], m["shell_dark"],
                scale=(ORB.radii.x * 0.985, ORB.radii.y * 0.99), segments=40)
    bpy.context.view_layer.update()
    # The swirl: a dark bar laid on the orb's surface.
    surface = mk.surface([ball])
    pts = []
    for x, y in mk.chaikin(SWIRL, 2, closed=False):
        hit = surface(x, y)
        pts.append(Vector((x, y, (hit[0].z if hit else 7.0) - 0.12)))
    swirl = thin_tube("swirl", pts, 0.34, m["swirl"], 5, squash=0.6, iterations=0)
    return [ball, rim, swirl]


def streaks(m, surface):
    pts = on(surface, mk.chaikin(STREAK, 1, closed=False), -0.12)
    return [thin_tube("streak_l", pts, 0.5, m["streak"], 6, squash=0.65, iterations=0)]


def body(m):
    obj = loft_top("body", body_table, BODY_Y, body_top, BODY_POWER, m["body"], 28, 40)

    mk.paint(obj, lambda c, n: m["body_dark"] if n.z < 0.12 else None)
    return obj


def seam(m, surface):
    return thin_tube("seam", on(surface, SEAM, -0.15), 0.42, m["body_dark"], 6, squash=0.6, iterations=1)


def cowl(m, surface):
    pts = [Vector(p) for p in on(surface, mk.chaikin(COWL, 2, closed=False), -0.45)]
    rings = []
    n = len(pts)
    segments = 12
    for i, p in enumerate(pts):
        a, b = pts[max(i - 1, 0)], pts[min(i + 1, n - 1)]
        t = Vector((b.x - a.x, b.y - a.y, 0.0)).normalized()
        side = Vector((-t.y, t.x, 0.0))
        ring = []
        for j in range(segments):
            ang = 2 * math.pi * j / segments
            c, s = math.cos(ang), math.sin(ang)
            u = math.copysign(abs(c) ** (2 / 2.6), c)
            v = math.copysign(abs(s) ** (2 / 2.6), s)
            ring.append(p + side * (u * COWL_HW) + Vector((0, 0, max(v * (COWL_H if s >= 0 else 0.7), 0.4 - p.z))))
        rings.append(ring)
    obj = k.loft("cowl", rings, m["cowl"], start_point=pts[0] + Vector((0, -0.4, 0)),
                 end_point=pts[-1] + Vector((0, -0.4, 0)))
    k.smooth(obj, 55)
    mk.paint(obj, lambda c, n: m["body_dark"] if n.z < 0.12 else None)
    hit = surface(TIP.centre.x, TIP.centre.y)
    z = (hit[0].z if hit else 3.5) - 0.55
    tip = painted_ball("tip", Ellipsoid((TIP.centre.x, TIP.centre.y, z), TIP.radii),
                       gem_paint((-0.5, -10.8), (0.7, 0.8), 0.7, (-0.6, -10.5), (0.35, 0.35), rim_z=0.3),
                       {"rim": m["streak"], "body": m["tip"], "light": m["tip"], "core": m["tip_hot"]},
                       subdivisions=3, smooth_angle=80)
    return [obj, tip]


def claws(m):
    obj, centres = horn("claw_l", CLAW, m["shell"], 10)
    paint_sections(obj, centres, 10, lambda c, n: m["seam"] if n.z < 0.1 or (n.x > 0.6 and n.z < 0.5) else
                   None)
    return [obj]


def machine():
    m = materials()
    wing = shell(m)
    bd = body(m)
    bpy.context.view_layer.update()
    surface = mk.surface([bd])
    parts = [bd, seam(m, surface)] + orb(m) + cowl(m, surface)
    left = [wing] + claws(m) + streaks(m, mk.surface([wing]))
    return parts + left + mirrored(left)


def own_mask(mask):
    """The machine's own pixels: the sprite's, with the swirl's pixels inside the orb (palette index 0, which the game
    draws see-through) counted as the orb's."""
    out = [row[:] for row in mask]
    for r in range(28):
        for c in range(24):
            x, y = c + 0.5 - 12, 13.5 - r
            if ((x - ORB.centre.x) / ORB.radii.x) ** 2 + ((y - ORB.centre.y) / ORB.radii.y) ** 2 < 0.92:
                out[r][c] = True
    return out


def build():
    options = k.args()
    out = mk.outdir(options)
    k.reset()
    parts = machine()
    triangulate(parts)
    bpy.context.view_layer.update()
    if "stats" in options:
        for obj in parts:
            print("  %-16s %5d triangles" % (obj.name, len(obj.data.polygons)))
    if "check" in options:
        sheet = os.path.join(options["check"], "enemy_V.png")
        covered = mk.coverage(parts, 24, 28)
        mask = k.sprite_mask(sheet, 161)
        mk.compare("swirl_machine (V 161)", covered, mask)
        mk.compare("swirl_machine (V 161, the swirl's see-through pixels counted)", covered, own_mask(mask))
    bpy.context.scene.view_settings.view_transform = "Standard"  # previews in the game's colours
    mk.report(NAME, parts, os.path.join(out, NAME + ".glb"))
    if "preview" in options:
        mk.preview(options["preview"] + NAME, parts, distance=0.7)


if __name__ == "__main__":
    build()
